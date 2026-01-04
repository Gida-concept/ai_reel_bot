import schedule
import time
import yaml
import subprocess
import sys
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger("scheduler")


class ReelScheduler:
    """
    Schedule and manage automated reel generation
    """

    def __init__(self, config_path: str = "settings.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.schedule_times = self.config['schedule']['times']
        logger.info(f"Scheduler initialized with times: {self.schedule_times}")

    def run_bot(self):
        """Execute the bot"""
        logger.info("\n" + "🎬" * 30)
        logger.info(f"Scheduled run triggered at {datetime.now()}")
        logger.info("🎬" * 30 + "\n")

        try:
            # Run main.py as subprocess
            result = subprocess.run(
                [sys.executable, "main.py"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                logger.info("✓ Bot execution successful")
            else:
                logger.error(f"❌ Bot execution failed with code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("❌ Bot execution timeout (10 minutes)")
        except Exception as e:
            logger.error(f"❌ Error running bot: {str(e)}")

    def start(self):
        """Start the scheduler"""
        logger.info("\n" + "=" * 60)
        logger.info("AI REEL AUTOMATION SCHEDULER STARTED")
        logger.info("=" * 60)

        # Schedule jobs
        for time_str in self.schedule_times:
            schedule.every().day.at(time_str).do(self.run_bot)
            logger.info(f"✓ Scheduled daily run at {time_str}")

        logger.info(f"\nNext run: {schedule.next_run()}")
        logger.info("Scheduler is now running. Press Ctrl+C to stop.\n")

        # Run loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\n\nScheduler stopped by user")
        except Exception as e:
            logger.error(f"\n\nScheduler crashed: {str(e)}")
            raise


def main():
    """Entry point for scheduler"""
    scheduler = ReelScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()