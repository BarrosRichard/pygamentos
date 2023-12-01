from dotenv import load_dotenv
import os

def env(var_name: str) -> str:
    load_dotenv(
        dotenv_path=os.path.join(
            os.path.dirname(
                os.path.dirname(
                   os.path.dirname(__file__)
                )
            ), ".env"
        )
    )
    return os.getenv(var_name)