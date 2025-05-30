import unittest

from electricitymap.contrib.config.model import (
    CO2EQ_CONFIG_MODEL,
    CONFIG_MODEL,
    ExchangeParsers,
    Parsers,
)
from electricitymap.contrib.lib.data_types import ParserDataType


class ConfigModelTestcase(unittest.TestCase):
    def test_pydantic_model(self):
        self.assertIn("DK-BHM->SE-SE4", CONFIG_MODEL.exchanges.keys())
        self.assertIn("US-NW-PSCO", CONFIG_MODEL.zones.keys())
        self.assertIsNotNone(
            CONFIG_MODEL.zones["US-NW-PSCO"].parsers.get_function("production")
        )

    # Add well-known sources that don't require config-based references here
    GLOBAL_SOURCE_REFERENCES = {
        "BEIS 2021",
        "CEA 2022",
        "EIA 2020/BEIS 2021",
        "EU-ETS 2021",
        "EU-ETS, ENTSO-E 2021",
        "IEA 2019",
        "IEA 2020",
        'Oberschelp, Christopher, et al. "Global emission hotspots of coal power generation."',
    }

    def test_zone_sources(self):
        for measurement_basis, model in CO2EQ_CONFIG_MODEL:
            for zone_key, zone_modes in model.emission_factors.zone_overrides.items():
                zone_sources = CONFIG_MODEL.zones[zone_key].sources
                for mode, estimate in zone_modes or ():
                    if estimate is None:
                        continue
                    estimates = estimate if isinstance(estimate, list) else [estimate]
                    for estimate in estimates:
                        self.assertIsNotNone(
                            estimate.source,
                            msg=f"{zone_key}: missing required field: emissionFactors.{measurement_basis}.{mode}.source",
                        )
                        for source in estimate.source.split(";"):
                            source = source.strip()
                            if source.startswith("assumes"):
                                continue
                            if source.startswith("Electricity Maps"):
                                continue
                            if source in self.GLOBAL_SOURCE_REFERENCES:
                                continue
                            self.assertIsNotNone(
                                zone_sources,
                                msg=f"{zone_key}: missing required field: sources",
                            )
                            assert zone_sources is not None  # pyright type-narrowing
                            self.assertIn(source, zone_sources, f"zone: {zone_key}")

    def test_parser_model_contains_all_parser_data_types(self):
        dummy_parser_model = Parsers()
        # Check 1:1 match between ParserDataType enum and Parsers model, except for exchange parsers, as they're defined in a different model
        all_parser_data_types = {
            dt.value for dt in ParserDataType if "exchange" not in dt.value
        }
        all_parser_model_fields = set(dummy_parser_model.__fields__.keys())
        self.assertEqual(all_parser_data_types, all_parser_model_fields)

    def test_exchange_parsers_model_contains_all_parser_data_types(self):
        dummy_exchange_parsers_model = ExchangeParsers()
        # Check 1:1 match between ParserDataType enum and ExchangeParsers model
        all_parser_data_types = {
            dt.value for dt in ParserDataType if "exchange" in dt.value
        }
        all_parser_model_fields = set(dummy_exchange_parsers_model.__fields__.keys())
        self.assertEqual(all_parser_data_types, all_parser_model_fields)


if __name__ == "__main__":
    unittest.main(buffer=True)
