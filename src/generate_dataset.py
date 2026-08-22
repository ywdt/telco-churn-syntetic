import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Union

# Compatibility patch for Python 3.14+ argparse in Hydra
try:
    import hydra_patch  # noqa: F401
except ImportError:
    from src import hydra_patch  # noqa: F401
import hydra
from omegaconf import DictConfig, OmegaConf

fake = Faker()
random.seed(42)
np.random.seed(42)


def _get_config_dict(config: Union[DictConfig, Dict[str, Any], None]) -> Dict[str, Any]:
    if config is None:
        return {}
    if isinstance(config, DictConfig):
        return OmegaConf.to_container(config, resolve=True)  # type: ignore
    return config


def generate_telco_dataset_with_drift(
    n_samples: int = 50000,
    start_date: str = "2023-01-01",
    end_date: str = "2024-12-31",
    output_file: str = "data/telco_churn_demo.csv",
    drift_config: dict = None,
    pricing_config: dict = None,
):
    drift = drift_config or {}
    pricing = pricing_config or {}

    fiber_growth_rate      = drift.get("fiber_growth_rate", 0.25)
    dsl_decline_rate       = drift.get("dsl_decline_rate", 0.20)
    no_inet_decline        = drift.get("no_internet_decline", 0.05)
    echeck_decline_rate    = drift.get("echeck_decline_rate", 0.25)
    m2m_decline_rate       = drift.get("m2m_decline_rate", 0.25)
    streaming_boost_factor = drift.get("streaming_boost_factor", 0.3)
    senior_decline_rate    = drift.get("senior_decline_rate", 0.12)
    churn_base_decline     = drift.get("churn_base_decline", 0.20)

    base_charge                 = pricing.get("base_charge", 20.0)
    phone_addon                 = pricing.get("phone_addon", 25.0)
    multiple_lines_addon        = pricing.get("multiple_lines_addon", 18.0)
    dsl_addon                   = pricing.get("dsl_addon", 50.0)
    fiber_base                  = pricing.get("fiber_base", 82.0)
    fiber_progress_bonus        = pricing.get("fiber_progress_bonus", 10.0)
    extra_service_per_item      = pricing.get("extra_service_per_item", 8.0)
    extra_service_progress_bonus= pricing.get("extra_service_progress_bonus", 3.0)
    one_year_discount           = pricing.get("one_year_discount", 0.94)
    two_year_discount           = pricing.get("two_year_discount", 0.88)
    two_year_progress_penalty   = pricing.get("two_year_progress_penalty", 0.03)

    data = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days

    for _ in range(n_samples):
        # Випадкова дата в діапазоні
        record_date = start + timedelta(days=random.randint(0, total_days))
        progress = (record_date - start).days / total_days  # 0.0 → 1.0 (2023 → 2024)

        # === ДРЕЙФ ПАРАМЕТРІВ ===
        fiber_prob = 0.40 + fiber_growth_rate * progress
        dsl_prob = 0.40 - dsl_decline_rate * progress
        no_inet_prob = 0.20 - no_inet_decline * progress

        echeck_prob = max(0.15, 0.40 - echeck_decline_rate * progress)
        m2m_prob = max(0.30, 0.55 - m2m_decline_rate * progress)
        streaming_boost = streaming_boost_factor * progress
        senior_prob = max(0.08, 0.18 - senior_decline_rate * progress)

        # === Генерація клієнта ===
        gender = random.choice(["Male", "Female"])
        senior_citizen = 1 if random.random() < senior_prob else 0
        has_partner = random.choices(["Yes", "No"], weights=[52 + 10*progress, 48 - 10*progress])[0]
        has_dependents = "Yes" if random.random() < (0.3 - 0.1*progress) else "No"

        tenure = int(np.random.beta(2 + progress, 3 - 0.5*progress) * 72)
        tenure = max(0, min(tenure, 72))

        phone_service = "Yes" if random.random() < 0.92 else "No"
        internet_service = random.choices(
            ["DSL", "Fiber optic", "No"],
            weights=[dsl_prob, fiber_prob, no_inet_prob]
        )[0]

        # Додаткові послуги
        if internet_service == "No":
            secs = ["No internet service"] * 6
            online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies = secs
        else:
            base_yes = 0.5 + streaming_boost
            online_security = "Yes" if random.random() < (base_yes * 0.7) else "No"
            online_backup = "Yes" if random.random() < (base_yes * 0.8) else "No"
            device_protection = "Yes" if random.random() < (base_yes * 0.75) else "No"
            tech_support = "Yes" if random.random() < (base_yes * 0.6) else "No"
            streaming_tv = "Yes" if random.random() < (base_yes + 0.1) else "No"
            streaming_movies = "Yes" if random.random() < (base_yes + 0.1) else "No"

        multiple_lines = "No phone service" if phone_service == "No" else (
            "Yes" if random.random() < 0.45 + 0.1*progress else "No"
        )

        # Контракт
        contract = random.choices(
            ["Month-to-month", "One year", "Two year"],
            weights=[m2m_prob, (1-m2m_prob)*0.6, (1-m2m_prob)*0.4]
        )[0]

        paperless_billing = "Yes" if random.random() < 0.59 + 0.15*progress else "No"

        payment_method = random.choices(
            ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
            weights=[echeck_prob, 0.25, 0.25 + 0.1*progress, 0.25 + 0.15*progress]
        )[0]

        # Ціна
        base = base_charge
        if phone_service == "Yes":
            base += phone_addon
            if multiple_lines == "Yes":
                base += multiple_lines_addon
        if internet_service == "DSL":
            base += dsl_addon
        elif internet_service == "Fiber optic":
            base += fiber_base + fiber_progress_bonus * progress

        extra_count = sum([online_security=="Yes", online_backup=="Yes", device_protection=="Yes",
                          tech_support=="Yes", streaming_tv=="Yes", streaming_movies=="Yes"])
        base += extra_count * (extra_service_per_item + extra_service_progress_bonus * progress)

        if contract == "One year":
            base *= one_year_discount
        elif contract == "Two year":
            base *= two_year_discount - two_year_progress_penalty * progress

        monthly_charges = round(max(18.5, base + np.random.normal(0, 6)), 2)
        total_charges = round(monthly_charges * tenure * random.uniform(0.97, 1.03), 2)

        # Churn — знижується з часом (компанія покращує сервіс)
        churn_base = 0.45
        if contract == "Month-to-month": churn_base += 0.35
        if payment_method == "Electronic check": churn_base += 0.18
        if internet_service == "Fiber optic": churn_base += 0.08
        if tenure < 12: churn_base += 0.25 - tenure*0.02
        churn_base -= churn_base_decline * progress

        churn = "Yes" if random.random() < churn_base else "No"

        customer_id = f"{random.randint(1000,9999)}-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}"

        row = [customer_id, gender, senior_citizen, has_partner, has_dependents, tenure,
               phone_service, multiple_lines, internet_service, online_security, online_backup,
               device_protection, tech_support, streaming_tv, streaming_movies, contract,
               paperless_billing, payment_method, monthly_charges, total_charges, churn,
               record_date.strftime("%Y-%m-%d")]

        data.append(row)

    columns = ["customerID","gender","SeniorCitizen","Partner","Dependents","tenure","PhoneService",
               "MultipleLines","InternetService","OnlineSecurity","OnlineBackup","DeviceProtection",
               "TechSupport","StreamingTV","StreamingMovies","Contract","PaperlessBilling",
               "PaymentMethod","MonthlyCharges","TotalCharges","Churn","RecordDate"]

    df = pd.DataFrame(data, columns=columns)
    df = df.sort_values("RecordDate").reset_index(drop=True)

    out_p = Path(output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_p, index=False)
    print(f"Готово! Згенеровано {n_samples:,} записів з дрейфом за {start_date}–{end_date}")
    print(f"Файл: {out_p}")
    print("\nРозподіл Churn по роках:")
    df['Year'] = pd.to_datetime(df['RecordDate']).dt.year
    print(df.groupby('Year')['Churn'].value_counts(normalize=True).unstack().round(3))


# === ЗАПУСК ЧЕРЕЗ HYDRA ===
@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig) -> None:
    output_dir_str = cfg.generation.get("output_dir", "data")
    output_path = Path(hydra.utils.to_absolute_path(output_dir_str))
    output_file = output_path / "telco_churn_demo.csv"

    n_samples = cfg.generation.get("samples", 50000)
    start_date = cfg.generation.get("start_date", "2023-01-01")
    end_date = cfg.generation.get("end_date", "2024-12-31")

    drift_cfg = _get_config_dict(cfg.get("drift", {}))
    pricing_cfg = _get_config_dict(cfg.get("pricing", {}))

    generate_telco_dataset_with_drift(
        n_samples=n_samples,
        start_date=start_date,
        end_date=end_date,
        output_file=str(output_file),
        drift_config=drift_cfg,
        pricing_config=pricing_cfg,
    )


if __name__ == "__main__":
    main()
