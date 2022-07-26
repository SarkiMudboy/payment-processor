import logging

logger: logging.Logger
logger.setLevel(logging.DEBUG)

def start():
	logging.info('Payment Processor started')
