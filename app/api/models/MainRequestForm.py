class MainRequestForm:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.errors = []

    async def load_data(self, latitude: str, longitude: str):
        is_valid_flag = False

        try:
            latitude, longitude  = str(latitude), str(longitude)
            latitude, longitude = latitude.replace(',', '.'), longitude.replace(',', '.')
            latitude_is_flaot = await self.is_float(latitude)
            longitude_is_float = await self.is_float(longitude)

            if latitude_is_flaot and longitude_is_float:
                latitude_valid_range = await self.is_valid_range(float(latitude), -90, 90)
                longitude_valid_range = await self.is_valid_range(float(longitude), -90, 90)

                if latitude_valid_range and longitude_valid_range:
                    self.latitude = float(latitude)
                    self.longitude = float(longitude)
                    is_valid_flag = True
        except Exception as e:
            print(e)
            self.errors.append("Value is not correct")

        return is_valid_flag

    async def is_valid_range(self, value, min_val, max_val):
        if value < min_val or value > max_val:
            self.errors.append(f"Value {value} out of range [{min_val}:{max_val}]")
            return False
        return True
    
    async def is_float(self, value):
        is_float_flag = False
        try:
            value = float(value)
            is_float_flag = True
        except Exception as e:
            self.errors.append(f"Value {value} is not float")
        return is_float_flag