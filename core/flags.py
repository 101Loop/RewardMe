from flags.state import flag_enabled


class FlagSources:
    ENABLE_OTP: str = "ENABLE_OTP"

    @classmethod
    def otp_enabled(cls) -> bool:
        return flag_enabled(cls.ENABLE_OTP)

    def get_flags(self, sources=None):
        return {
            self.ENABLE_OTP: [],
        }
