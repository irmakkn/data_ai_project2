from llm.finance_llm import analyze_finance
from llm.healthcare_llm import analyze_healthcare
from llm.retail_llm import analyze_retail
from llm.generic_llm import analyze_generic


def route_llm(sector: str, profile, columns, rows, sample_rows):

    sector = sector.lower()

    if "finance" in sector:
        return analyze_finance(profile, columns, rows, sample_rows)

    elif "health" in sector:
        return analyze_healthcare(profile, columns, rows, sample_rows)

    elif "retail" in sector:
        return analyze_retail(profile, columns, rows, sample_rows)

    else:
        return analyze_generic(profile, columns, rows, sample_rows)
