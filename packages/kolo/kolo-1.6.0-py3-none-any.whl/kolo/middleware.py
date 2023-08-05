import logging
import os
import sys
import threading
from typing import Any, Callable, Dict, Tuple

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .config import create_kolo_directory, load_config_from_toml
from .db import load_config_from_db, setup_db
from .profiler import KoloProfiler

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]


class KoloMiddleware:
    def __init__(self, get_response: DjangoView) -> None:
        self._get_response = get_response
        self.enabled = self.should_enable()
        if self.enabled:
            kolo_directory = create_kolo_directory()
            self.config = load_config_from_toml(kolo_directory / "config.toml")
            self.db_path = setup_db(self.config)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.enabled or self.check_for_third_party_profiler():
            return self.get_response(request)

        self.config = load_config_from_db(self.db_path, self.config)
        self.use_frame_boundaries = self.config.get("use_frame_boundaries", False)

        filter_config = self.config.get("filters", {})
        ignore_request_paths = filter_config.get("ignore_request_paths", [])
        for path in ignore_request_paths:
            if path in request.path:
                return self.get_response(request)

        self.profiler = KoloProfiler(self.db_path, config=self.config)
        if not self.use_frame_boundaries:
            self.profiler.initialize_request(request)

        with self.profiler:
            response = self.get_response(request)

        if not self.use_frame_boundaries:
            self.profiler.finalize_response(response)

        threading.Thread(
            target=self.profiler.save_request_in_db, name="kolo-save_request_in_db"
        ).start()

        return response

    def process_view(
        self,
        request: HttpRequest,
        view_func: DjangoView,
        view_args: Tuple[Any],
        view_kwargs: Dict[str, Any],
    ):
        if self.enabled and not self.use_frame_boundaries:
            self.profiler.set_url_pattern(request)

    def get_response(self, request: HttpRequest) -> HttpResponse:
        response = self._get_response(request)
        return response

    def check_for_third_party_profiler(self) -> bool:
        profiler = sys.getprofile()
        if profiler:
            logger.warning("Profiler %s is active, disabling KoloMiddleware", profiler)
            return True
        return False

    def should_enable(self) -> bool:
        if settings.DEBUG is False:
            logger.debug("DEBUG mode is off, disabling KoloMiddleware")
            return False

        if os.environ.get("KOLO_DISABLE", "false").lower() not in ["false", "0"]:
            logger.debug("KOLO_DISABLE is set, disabling KoloMiddleware")
            return False

        if self.check_for_third_party_profiler():
            return False

        return True
