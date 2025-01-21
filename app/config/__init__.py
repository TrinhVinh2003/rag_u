import logging
import logging.config
import os
import yaml
from typing import Optional


class LoggerSetup:
    """
    Class để cấu hình hệ thống logging.
    """

    @staticmethod
    def ensure_log_folder_exists(log_dir: str = "log") -> None:
        """
        Đảm bảo folder log tồn tại. Tạo folder nếu cần thiết.
        :param log_dir: Đường dẫn tới folder log
        """
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Không thể tạo folder log: {log_dir}. Chi tiết: {e}")

    @staticmethod
    def load_config_from_yaml(config_path: str) -> Optional[dict]:
        """
        Nạp cấu hình logging từ file YAML.
        :param config_path: Đường dẫn tới file YAML
        :return: Cấu hình logging dưới dạng dictionary hoặc None nếu lỗi
        """
        if not os.path.exists(config_path):
            logging.warning(f"File cấu hình logging không tồn tại: {config_path}")
            return None

        try:
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logging.error(f"Lỗi khi đọc file YAML: {e}")
            return None

    @staticmethod
    def setup_logging(config_path: Optional[str] = None, default_level: int = logging.INFO) -> None:
        """
        Thiết lập logging từ file cấu hình YAML hoặc fallback sang cấu hình mặc định.
        :param config_path: Đường dẫn tới file cấu hình YAML
        :param default_level: Level logging mặc định nếu không tìm thấy file YAML.
        """  # noqa: D205
        
        # Đảm bảo folder log tồn tại
        LoggerSetup.ensure_log_folder_exists()

        # Nạp cấu hình từ YAML
        if config_path:
            config = LoggerSetup.load_config_from_yaml(config_path)
            if config:
                logging.config.dictConfig(config)
                logging.info(f"Logging được cấu hình từ file: {config_path}")
                return

        # Fallback sang cấu hình mặc định
        logging.basicConfig(
            level=default_level,
            format="%(asctime)s %(levelname)-8s --- %(name)-40s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.warning("Đang sử dụng cấu hình logging mặc định!")


