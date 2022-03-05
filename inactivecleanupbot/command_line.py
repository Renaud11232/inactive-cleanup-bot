import argparse
from inactivecleanupbot import InactiveCleanupBot


def main():
    parser = argparse.ArgumentParser(description="Runs the inactive-cleanup-bot")
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()
    bot = InactiveCleanupBot(args.config)
    bot.run()
