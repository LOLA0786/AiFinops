class GPUTaxEngine:
    def __init__(self):
        self.tax_rate = 0.05

    def collect(self, region_gdp):
        tax_revenue = {}
        for region, gdp in region_gdp.items():
            tax_revenue[region] = gdp * self.tax_rate
        return tax_revenue
