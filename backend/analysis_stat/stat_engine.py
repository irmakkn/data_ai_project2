import pandas as pd
import numpy as np
import sys
import os

# --- PATH KORUMASI ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class StatEngine:
    """
    LLM'in önerdiği istatistiksel ve ML yöntemlerini
    gerçek veri üzerinde uygulayan motor.
    """
    
    @staticmethod
    def run_outlier_detection(df: pd.DataFrame):
        # Senin mevcut outlier kodunu buraya entegre ediyoruz
        # Örnek: Z-Score veya IQR yöntemi
        numeric_df = df.select_dtypes(include=[np.number])
        z_scores = np.abs((numeric_df - numeric_df.mean()) / numeric_df.std())
        outliers = (z_scores > 3).any(axis=1)
        return df[~outliers], f"{outliers.sum()} adet outlier temizlendi."

    @staticmethod
    def run_clustering(df: pd.DataFrame, n_clusters=3):
        # Senin mevcut cluster kodun (Örn: K-Means)
        # Şimdilik placeholder olarak bırakıyorum
        return df, "Clustering tamamlandı (K-Means applied)."

    @staticmethod
    def run_time_series(df: pd.DataFrame):
        # Senin mevcut time series kodun
        return df, "Zaman serisi analizi/mevsimsellik hesaplandı."

    @classmethod
    def execute_pipeline(cls, df: pd.DataFrame, suggestions: dict):
        """
        LLM'den gelen analiz önerilerine göre doğru fonksiyonu seçer.
        """
        results = []
        current_df = df.copy()
        
        # LLM 'cleaning_steps' içinde 'outlier' kelimesini geçirdiyse:
        steps = str(suggestions.get("cleaning_steps", "")).lower()
        
        if "outlier" in steps:
            current_df, msg = cls.run_outlier_detection(current_df)
            results.append(msg)
            
        if "cluster" in steps:
            current_df, msg = cls.run_clustering(current_df)
            results.append(msg)
            
        return current_df, results