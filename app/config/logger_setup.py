import logging
import logging.config
import os
from pathlib import Path

import yaml


class LoggerSetup:
    """Cấu hình logging cho ứng dụng từ file cấu hình YAML."""

    @staticmethod
    def setup_logging(config_path: str) -> None:
        """
        Thiết lập cấu hình logging từ file YAML.

        Args:
            config_path (str): Đường dẫn tới file cấu hình YAML.
            log_dir (str, optional): Thư mục lưu log. Mặc định là "logs".

        Raises:
            FileNotFoundError: Nếu không tìm thấy file cấu hình.
            yaml.YAMLError: Nếu cấu hình không hợp lệ.
            Exception: Nếu có lỗi khi cấu hình logger.
        """
        # Đảm bảo folder log tồn tại
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Nạp cấu hình logging từ file YAML
        with Path.open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

        # Kiểm tra cấu hình đã thành công
        logging.info(f"Logging đã được cấu hình từ file: {config_path}")
