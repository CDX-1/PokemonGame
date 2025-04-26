from src.pokemon.types.ball import Ball


class CaptureData:
    def __init__(
            self,
            ball: Ball,
            original_trainer: str
    ):
        self.ball = ball
        self.original_trainer = original_trainer