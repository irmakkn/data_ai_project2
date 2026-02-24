import matplotlib.pyplot as plt
import pandas as pd
import base64
import io


def execute_pipeline(df: pd.DataFrame, cleaning_code: str, visualization_code: str):
    """
    LLM tarafından üretilen kodu kontrollü şekilde çalıştırır.
    """

    local_env = {
        "df": df.copy(),
        "pd": pd,
        "plt": plt
    }

    # 1️⃣ Cleaning çalıştır
    if cleaning_code:
        exec(cleaning_code, {}, local_env)

    cleaned_df = local_env.get("df")

    # 2️⃣ Visualization çalıştır
    img_base64 = None

    if visualization_code:
        plt.figure()
        exec(visualization_code, {}, local_env)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()

    return cleaned_df, img_base64
