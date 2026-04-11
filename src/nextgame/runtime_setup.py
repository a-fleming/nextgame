import logging

from pathlib import Path

from nextgame.config import Settings

def configure_logging(settings: Settings) -> None:
    log_path = Path(settings.log_path).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(log_path),
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
