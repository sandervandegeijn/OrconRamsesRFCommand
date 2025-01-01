import logging

logger = logging.getLogger(__name__)


class OrconRamsesRFCommand:
    """
    This class controls an Orcon HVAC unit via Ramses_RF.
    """

    def __init__(self, remote_address, wtw_address, capacity_in_m3_per_hour=400):
        """
        :param remote_address: The address of the remote (e.g. "37:11111")
        :param wtw_address: The address of the WTW unit (e.g. "32:222222")
        """
        self.remote = remote_address
        self.wtw = wtw_address
        self.capacity_in_m3_per_hour = capacity_in_m3_per_hour
        self.logger = logger

    def _fan_speed_payload(self, param: int, speed_percentage: int) -> str:
        """
        Build the hex payload for the 'W --- 37:... 32:... --:------ 2411 023 ...' message.
        This payload sets the speed for a given parameter (3 through 8).

        The speed is encoded at twice the percentage 
        (e.g. 28% → 56 decimal → 0x38 in hex).
        
        :param param: The parameter number (3..8).
        :param speed_percentage: The speed percentage (1..100).
        :return: The hex string payload (without spacing).
        :raises ValueError: if param or speed_percentage are out of range.
        """
        param_suffix = {
            3: "00000000000000A0000000010032",
            4: "00000000000000A0000000010032",
            5: "00000000000000C8000000010032",
            6: "0000000014000000C8000000010032",
            7: "00000000000000C8000000010032",  # Corrected suffix for parameter 7
            8: "00000014000000C8000000010032"   # Corrected suffix for parameter 8
        }

        if not (3 <= param <= 8):
            raise ValueError("Parameter must be between 3 and 8.")
        if not (1 <= speed_percentage <= 100):
            raise ValueError("Speed percentage must be between 1 and 100.")

        # Calculate the ParamID (offset by 0x3C from the parameter).
        param_id = param + 0x3C

        # Multiply the speed percentage by 2 to get the hex value.
        speed_hex = f"{speed_percentage * 2:02X}"

        # The prefix is typically "0000{ParamID}000F000000{speed_hex}" 
        # based on the observed logs.
        prefix = f"0000{param_id:02X}000F000000{speed_hex}"

        # Get the suffix from the dictionary for this parameter.
        suffix = param_suffix[param]

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return msg
    
    def _calculate_percentage_from_m3_per_hour(self, m3_per_hour: int) -> int:
        """
        Calculate the fan speed percentage based on the given flow rate in m³/h.
        The percentage is calculated as a ratio of the given flow rate to the unit's capacity.

        :param m3_per_hour: The flow rate in m³/h.
        :return: The fan speed percentage.
        """
        return int((m3_per_hour / self.capacity_in_m3_per_hour) * 100)
        

    def set_fan_speed(self, level_name: str, m3_per_hour: int):
        """
        Set the fan speed level for the given level name
        to the specified speed percentage.
        """
        lvl = level_name.lower()

        percentage = self._calculate_percentage_from_m3_per_hour(m3_per_hour)
        self.logger.debug(f"Calculated percentage: {percentage}")

        if lvl == "low":
            # param 3: Low supply, param 4: Low extraction
            msg3 = self._fan_speed_payload(3, percentage)
            msg4 = self._fan_speed_payload(4, percentage)
            return [msg3, msg4]

        elif lvl == "medium":
            # param 5: Medium supply, param 6: Medium extraction
            msg5 = self._fan_speed_payload(5, percentage)
            msg6 = self._fan_speed_payload(6, percentage)
            return [msg5, msg6]

        elif  lvl == "high":
            # param 7: High supply, param 8: High extraction
            msg7 = self._fan_speed_payload(7, percentage)
            msg8 = self._fan_speed_payload(8, percentage)
            return [msg7, msg8]

        else:
            raise ValueError("level_name must be 'low/medium/high.")

    def turn_fan_off(self) -> str:
        """
        Generate the command to turn the ventilation unit off.

        :return: The command string to turn off the unit.
        """
        self.logger.info("Turning the unit off.")
        payload = "000007"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_low_mode(self) -> str:
        """
        Generate the command to set the unit to low mode.

        :return: The command string for low mode.
        """
        self.logger.info("Setting the unit to low mode.")
        payload = "000104"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_medium_mode(self) -> str:
        """
        Generate the command to set the unit to medium mode.

        :return: The command string for medium mode.
        """
        self.logger.info("Setting the unit to medium mode.")
        payload = "000204"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_high_mode(self) -> str:
        """
        Generate the command to set the unit to high mode.

        :return: The command string for high mode.
        """
        self.logger.info("Setting the unit to high mode.")
        payload = "000304"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_auto_mode(self) -> str:
        """
        Generate the command to set the unit to auto mode.

        :return: The command string for auto mode.
        """
        self.logger.info("Setting the unit to auto mode.")  
        payload = "000407"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_auto2_mode(self) -> str:
        """
        Generate the command to set the unit to auto2 mode.

        :return: The command string for auto2 mode.
        """
        self.logger.info("Setting the unit to auto2 mode.")
        payload = "000507"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def set_to_boost_mode(self) -> str:
        """
        Generate the command to set the unit to boost mode.

        :return: The command string for boost mode.
        """
        self.logger.info("Setting the unit to boost mode.")
        payload = "000607"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def disable_mode(self) -> str:
        """
        Generate the command to disable the unit.

        :return: The command string to disable the unit.
        """
        self.logger.info("Disabling the unit.")
        payload = "000707"
        msg = (
            f"I --- {self.remote} {self.wtw} --:------ "
            f"22F1 003 {payload}"
        )
        return [msg]

    def open_bypass(self) -> str:
        """
        Generate the command to open the bypass.

        :return: The command string to open the bypass.
        """
        self.logger.info("Open bypass")
        payload = "00C8EF"
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"22F7 003 {payload}"
        )
        return [msg]

    def close_bypass(self) -> str:
        """
        Generate the command to close the bypass.

        :return: The command string to close the bypass.
        """
        self.logger.info("Close bypass")
        payload = "0000EF"
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"22F7 003 {payload}"
        )
        return [msg]

    def automatic_bypass(self) -> str:
        """
        Generate the command to set the bypass to auto mode.

        :return: The command string to set bypass to auto.
        """
        self.logger.info("Automatic bypass mode")
        payload = "00FFEF"
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"22F7 003 {payload}"
        )
        return [msg]
   ##### 
    def set_absence_supply_fan_speed(self, speed_percentage: int) -> str:
        """
        Generate the command payload to set the absence supply fan speed (Parameter 1).

        This function controls the fan speed percentage for the supply fan 
        in absence mode. The value ranges from 0% to 40%, and is encoded 
        as twice the percentage value in the payload.

        :param speed_percentage: The desired fan speed percentage (0..40).
        :return: The command string to set the absence supply fan speed.
        :raises ValueError: if speed_percentage is out of range.
        """
        if not (0 <= speed_percentage <= 40):
            raise ValueError("Speed percentage for absence supply fan must be between 0 and 40.")

        # Calculate the ParamID for Parameter 1 (fixed as 0x3D).
        param_id = 0x3D

        # Multiply the speed percentage by 2 to get the hex representation.
        speed_hex = f"{speed_percentage * 2:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}000F000000{speed_hex}"

        # Fixed suffix for Parameter 1 based on patterns in data.
        suffix = "0000000000000050000000010032"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_absence_exhaust_fan_speed(self, speed_percentage: int) -> str:
        """
        Generate the command payload to set the absence exhaust fan speed (Parameter 2).

        This function controls the fan speed percentage for the exhaust fan 
        in absence mode. The value ranges from 0% to 40%, and is encoded 
        as twice the percentage value in the payload.

        :param speed_percentage: The desired fan speed percentage (0..40).
        :return: The command string to set the absence exhaust fan speed.
        :raises ValueError: if speed_percentage is out of range.
        """
        if not (0 <= speed_percentage <= 40):
            raise ValueError("Speed percentage for absence exhaust fan must be between 0 and 40.")

        # Calculate the ParamID for Parameter 2 (fixed as 0x3E).
        param_id = 0x3E

        # Multiply the speed percentage by 2 to get the hex representation.
        speed_hex = f"{speed_percentage * 2:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}000F000000{speed_hex}"

        # Fixed suffix for Parameter 2 based on patterns in data.
        suffix = "0000000000000050000000010032"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_boost_mode_speed(self, speed_percentage: int) -> str:
        """
        Generate the command payload to set the boost mode fan speed (Parameter 9).

        This function controls the fan speed percentage for boost mode. 
        The value ranges from 0% to 100%, and is encoded as twice the percentage value in the payload.

        :param speed_percentage: The desired fan speed percentage (0..100).
        :return: The command string to set the boost mode fan speed.
        :raises ValueError: if speed_percentage is out of range.
        """
        if not (0 <= speed_percentage <= 100):
            raise ValueError("Speed percentage for boost mode must be between 0 and 100.")

        # Calculate the ParamID for Parameter 9 (fixed as 0x95).
        param_id = 0x95

        # Multiply the speed percentage by 2 to get the hex representation.
        speed_hex = f"{speed_percentage * 2:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}000F000000{speed_hex}"

        # Fixed suffix for Parameter 9 based on patterns in data.
        suffix = "00000000000000C8000000010032"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_filter_replacement_time(self, days: int) -> str:
        """
        Generate the command payload to set the time until filter replacement (Parameter 10).

        This function sets the number of days until the filter replacement notification is triggered.
        The value ranges from 0 to 255 days and is encoded as its hexadecimal equivalent in the payload.

        Grepped commands:
        value 1:		W --- 37:ID 32:ID --:------ 2411 023 00004E0000000000010000000000000001000000010000
        value 0: 		W --- 37:ID 32:ID --:------ 2411 023 00004E0000000000000000000000000001000000010000

        :param days: The desired time until filter replacement in days (0..255).
        :return: The command string to set the filter replacement time.
        :raises ValueError: if days are out of range.
        """
        if not (0 <= days <= 255):
            raise ValueError("Filter replacement time must be between 0 and 255 days.")

        # Calculate the ParamID for Parameter 10 (fixed as 0x31).
        param_id = 0x31

        # Convert the number of days to its hexadecimal representation.
        days_hex = f"{days:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}0010000000{days_hex}"

        # Fixed suffix for Parameter 10 based on patterns in data.
        suffix = "000000000007080000001E002C"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_sensor_sensitivity(self, sensitivity: int) -> str:
        """
        Generate the command payload to set the sensor sensitivity (Parameter 12).

        This function controls the sensitivity of the sensor. The value can range from 0 to 15.

        Captured commands:
        value 6: 		W --- 37:ID 32:ID --:------ 2411 023 00005200010000003C00000000000000FA000000010032
        value 15:		W --- 37:ID 32:ID --:------ 2411 023 00005200010000009600000000000000FA000000010032
        value 5: 		W --- 37:ID 32:ID --:------ 2411 023 00005200010000003200000000000000FA000000010032

        :param sensitivity: The desired sensor sensitivity (0..15).
        :return: The command string to set the sensor sensitivity.
        :raises ValueError: if sensitivity is out of range.
        """
        if not (0 <= sensitivity <= 15):
            raise ValueError("Sensor sensitivity must be between 0 and 15.")

        # Calculate the ParamID for Parameter 12 (fixed as 0x52).
        param_id = 0x52

        # Multiply the sensitivity value by 6 to match observed encoding (e.g., 5 -> 0x32).
        sensitivity_hex = f"{sensitivity * 6:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}0001000000{sensitivity_hex}"

        # Fixed suffix for Parameter 12 based on patterns in data.
        suffix = "00000000000000FA000000010032"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_humidity_scenario_runtime(self, minutes: int) -> str:
        """
        Generate the command payload to set the runtime for the humidity scenario (Parameter 13).

        This function controls the overrun time for the humidity scenario in minutes.
        The value can range from 15 to 60 minutes.

        :param minutes: The desired overrun time in minutes (15..60).
        :return: The command string to set the humidity scenario runtime.
        :raises ValueError: if minutes are out of range.

        Captured data for Parameter 13:
        - Value 16: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000540000000000100000000F0000003C00000001002A
        - Value 20: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000540000000000140000000F0000003C00000001002A
        """
        if not (15 <= minutes <= 60):
            raise ValueError("Humidity scenario runtime must be between 15 and 60 minutes.")

        # Calculate the ParamID for Parameter 13 (fixed as 0x54).
        param_id = 0x54

        # Convert the number of minutes to its hexadecimal representation.
        minutes_hex = f"{minutes:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}0000000000{minutes_hex}"

        # Fixed suffix for Parameter 13 based on patterns in data.
        suffix = "0000000F0000003C00000001002A"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_comfort_temperature(self, temperature: float) -> str:
        """
        Generate the command payload to set the comfort temperature (Parameter 14).

        This function controls the comfort temperature setting in degrees Celsius.
        The value can range from 0.0°C to 30.0°C, with a resolution of 0.1°C.

        :param temperature: The desired comfort temperature in °C (0.0..30.0).
        :return: The command string to set the comfort temperature.
        :raises ValueError: if temperature is out of range.

        Captured data for Parameter 14:
        - Value 20.1: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000007DA0000000000000BB8000000010001
        - Value 20.5: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008020000000000000BB8000000010001
        - Value 22.3: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008B60000000000000BB8000000010001
        """
        if not (0.0 <= temperature <= 30.0):
            raise ValueError("Comfort temperature must be between 0.0 and 30.0°C.")

        # Calculate the ParamID for Parameter 14 (fixed as 0x75).
        param_id = 0x75

        # Convert the temperature to its hexadecimal representation (value * 10).
        temp_hex = f"{int(temperature * 10):04X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}0092000000{temp_hex}"

        # Fixed suffix for Parameter 14 based on patterns in data.
        suffix = "00000000000BB8000000010001"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]

    def set_min_fan_speed_bypass(self, speed_percentage: int) -> str:
        """
        Generate the command payload to set the minimum fan speed for bypass (Parameter 15).

        This function controls the minimum fan speed percentage when the bypass is active.
        The value can range from 0% to 30%, with a default of 15%.

        :param speed_percentage: The desired minimum fan speed percentage (0..30).
        :return: The command string to set the minimum fan speed for bypass.
        :raises ValueError: if speed_percentage is out of range.

        Captured data for Parameter 15:
        - Value 16: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000020000000000000003C000000010001
        - Value 20: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000028000000000000003C000000010001
        - Value 24: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000030000000000000003C000000010001
        """
        if not (0 <= speed_percentage <= 30):
            raise ValueError("Minimum fan speed for bypass must be between 0% and 30%.")

        # Calculate the ParamID for Parameter 15 (fixed as 0xA1).
        param_id = 0xA1

        # Convert the speed percentage to its hexadecimal representation (value * 2).
        speed_hex = f"{speed_percentage * 2:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}000F000000{speed_hex}"

        # Fixed suffix for Parameter 15 based on patterns in data.
        suffix = "00000000003C000000010001"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )
        return [msg]
