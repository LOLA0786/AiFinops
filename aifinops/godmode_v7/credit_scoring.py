class GPUCreditScore:
    def calculate(self, usage_history, missed_payments):
        score = 800 - (missed_payments * 50)
        score += sum(usage_history) * 0.1
        return max(300, min(900, score))
