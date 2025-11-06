import logging


class Logger:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.logger: logging.Logger = logging.getLogger(name) # __name__

    
    def configure(self) -> logging.Logger:
        if not self.logger.handlers:
            handler = logging.FileHandler(f'./logs/{self.name}.log', encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        return self.logger