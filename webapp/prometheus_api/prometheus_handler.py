"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from webapp.common.config import ConfigHelper
from webapp.common.events import EventHelper
from webapp.common.logging import Logger
from webapp.models.source import SourceStatus
from webapp.prometheus_api.prometheus_models import Metrics, MetricType, ParkingSiteMetric, SourceMetric
from webapp.repositories import ParkingSiteRepository, SourceRepository


class PrometheusHandler:
    logger: Logger
    config_helper: ConfigHelper
    event_helper: EventHelper
    source_repository: SourceRepository
    parking_site_repository: ParkingSiteRepository

    def __init__(
        self,
        logger: Logger,
        config_helper: ConfigHelper,
        event_helper: EventHelper,
        source_repository: SourceRepository,
        parking_site_repository: ParkingSiteRepository,
    ):
        self.logger = logger
        self.config_helper = config_helper
        self.event_helper = event_helper
        self.source_repository = source_repository
        self.parking_site_repository = parking_site_repository

    def get_metrics(self) -> str:
        sources = self.source_repository.fetch_sources()

        last_static_update_metrics = Metrics(
            help='Last static update in seconds from now',
            type=MetricType.gauge,
            identifier='app_park_api_source_last_static_update',
        )
        last_realtime_update_metrics = Metrics(
            help='Last realtime update in seconds from now',
            type=MetricType.gauge,
            identifier='app_park_api_source_last_realtime_update',
        )
        source_static_parking_site_errors = Metrics(
            help='Parking site static errors by source',
            type=MetricType.gauge,
            identifier='app_static_park_api_source_errors',
        )
        source_realtime_parking_site_errors = Metrics(
            help='Parking site realtime error by source',
            type=MetricType.gauge,
            identifier='app_realtime_park_api_source_errors',
        )
        failed_sources = Metrics(
            help='Completely failed sources',
            type=MetricType.gauge,
            identifier='app_park_api_source_failed',
        )
        for source in sources:
            if source.status in [SourceStatus.DISABLED, SourceStatus.PROVISIONED]:
                continue
            if source.static_data_updated_at:
                last_static_update_metrics.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=int((datetime.now(tz=timezone.utc) - source.static_data_updated_at).total_seconds()),
                    )
                )
            if source.realtime_data_updated_at:
                last_realtime_update_metrics.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=int((datetime.now(tz=timezone.utc) - source.realtime_data_updated_at).total_seconds()),
                    )
                )
            source_static_parking_site_errors.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=source.static_parking_site_error_count,
                )
            )
            source_realtime_parking_site_errors.metrics.append(
                SourceMetric(
                    source=source.uid,
                    value=source.realtime_parking_site_error_count,
                )
            )
            if source.status in [SourceStatus.FAILED, SourceStatus.ACTIVE]:
                failed_sources.metrics.append(
                    SourceMetric(
                        source=source.uid,
                        value=1 if source.status == SourceStatus.FAILED else 0,
                    )
                )

        metrics = (
            last_static_update_metrics.to_metrics()
            + last_realtime_update_metrics.to_metrics()
            + source_static_parking_site_errors.to_metrics()
            + source_realtime_parking_site_errors.to_metrics()
            + failed_sources.to_metrics()
        )

        if self.config_helper.get('PARKING_SITE_METRICS', False):
            metrics += self.get_parking_site_metrics()

        return '\n'.join(metrics)

    def get_parking_site_metrics(self) -> list[str]:
        parking_sites = self.parking_site_repository.fetch_parking_sites(include_source=True)

        parking_site_static_capacity = Metrics(
            help='Parking site static capacity',
            type=MetricType.gauge,
            identifier='app_park_api_parking_site_static_capacity',
        )
        parking_site_realtime_capacity = Metrics(
            help='Parking site realtime capacity',
            type=MetricType.gauge,
            identifier='app_park_api_parking_site_realtime_capacity',
        )

        for parking_site in parking_sites:
            parking_site_static_capacity.metrics.append(
                ParkingSiteMetric(
                    parking_site=parking_site.original_uid,
                    source=parking_site.source.uid,
                    value=parking_site.capacity,
                )
            )
            if parking_site.has_realtime_data:
                parking_site_realtime_capacity.metrics.append(
                    ParkingSiteMetric(
                        parking_site=parking_site.original_uid,
                        source=parking_site.source.uid,
                        value=parking_site.realtime_capacity,
                    )
                )

        return parking_site_static_capacity.to_metrics() + parking_site_realtime_capacity.to_metrics()
