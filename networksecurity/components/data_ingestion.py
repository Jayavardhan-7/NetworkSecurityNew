from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URI")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Read data from MongoDB collection and return as DataFrame.
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            logging.info(f"Connecting to MongoDB at: {MONGO_DB_URL}")
            mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            logging.info(f"Data loaded from collection: {collection_name}, shape: {df.shape}")

            if "_id" in df.columns:
                df = df.drop(columns=["_id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)

            logging.info("DataFrame sample:\n" + str(df.head()))
            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Save the DataFrame to a CSV file in the feature store location.
        """
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"Data exported to feature store at: {feature_store_file_path}")

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """
        Split the DataFrame into training and testing datasets.
        """
        try:
            if dataframe.empty:
                raise ValueError("Loaded DataFrame is empty. Cannot perform train/test split.")

            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Train-test split successful.")
            logging.info(f"Train shape: {train_set.shape}, Test shape: {test_set.shape}")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)

            logging.info(f"Train data saved to: {self.data_ingestion_config.training_file_path}")
            logging.info(f"Test data saved to: {self.data_ingestion_config.testing_file_path}")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Orchestrate the full data ingestion process.
        """
        try:
            logging.info("Starting data ingestion process...")

            dataframe = self.export_collection_as_dataframe()

            if dataframe.empty:
                raise ValueError("MongoDB collection returned an empty DataFrame.")

            dataframe = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            logging.info("Data ingestion process completed successfully.")
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
