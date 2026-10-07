import logging
import re
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class CustomerCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        logger.info("CustomerCleaner initialized.")

    def standardize_column_names(self):
        #MonthlyCharges -> monthly_charges

        def to_snake(name):
            name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
            name = name.replace(" ", "_")
            return name.lower()

        self.df.columns = [to_snake(col) for col in self.df.columns]

        logger.info("Column names standardized.")
        return self

    def fix_total_charges(self):
        try:
            if "total_charges" not in self.df.columns:
                logger.warning("Column 'total_charges' not found.")
                return self

            self.df["total_charges"] = (
                self.df["total_charges"]
                .replace(r'^\s*$', pd.NA, regex=True)
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            logger.info(
                "Converted total_charges to numeric."
            )

        except Exception as e:
            logger.error("Unexpected error in fix_total_charges(): %s", e)

        return self

    def normalize_binary_columns(self):
        #Converts Yes/No to 1/0.

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        mapping = {
            "Yes": 1,
            "No": 0
        }

        for col in binary_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].map(mapping)

        logger.info("Binary columns normalized.")

        return self

    def handle_nulls(self):
        """
        Fill missing total_charges using monthly_charges.
        Appropriate for new customers with tenure=0.
        """

        if (
            "total_charges" in self.df.columns and
            "monthly_charges" in self.df.columns
        ):

            self.df["total_charges"] = self.df["total_charges"].fillna(
                self.df["monthly_charges"]
            )

            logger.info(
                "Filled missing total_charges values using monthly_charges."
            )

        return self

    def clean(self):
        #Run all
        logger.info("Starting cleaning pipeline.")

        return (
            self
            .standardize_column_names()
            .fix_total_charges()
            .normalize_binary_columns()
            .handle_nulls()
            .df
        ) 
    #self object la function application ku apram ulla df return aaguthu

if __name__ == "__main__":

    df = pd.read_csv("./Telco-Customer-Churn.csv")

    logger.info("Before Cleaning")
    logger.info("Shape: %s", df.shape)
    logger.info("Dtypes:\n%s", df.dtypes)

    cleaner = CustomerCleaner(df)

    cleaned_df = cleaner.clean()

    logger.info("After Cleaning")
    logger.info("Shape: %s", cleaned_df.shape)
    logger.info("Dtypes:\n%s", cleaned_df.dtypes)

    #cleaned_df.to_csv("Cleaned_Telco_Churn.csv")
    #logger.info("Cleaned Data Exported")