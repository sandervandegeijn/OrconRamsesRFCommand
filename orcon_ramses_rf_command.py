import logging

logger = logging.getLogger(__name__)


class OrconRamsesRFCommand:
    """
    This class, `OrconRamsesRFCommand`, provides an interface for controlling an Orcon HVAC unit via Ramses_RF commands.

    Mapping Between Parameters and Functions:
    Each parameter corresponds to a specific setting in the Orcon HVAC system, and the class provides functions to control these settings.

        1. Absence Mode Supply Fan Speed (Parameter 1): Controlled by `set_absence_supply_fan_speed()`. Sets the supply fan speed in absence mode (0-40%).
        2. Absence Mode Exhaust Fan Speed (Parameter 2): Controlled by `set_absence_exhaust_fan_speed()`. Sets the exhaust fan speed in absence mode (0-40%).
        3. Low Supply Fan Speed (Parameter 3): Controlled via `set_fan_speed(level_name='low', ...)`. Adjusts the supply fan speed for low mode.
        4. Low Exhaust Fan Speed (Parameter 4): Controlled via `set_fan_speed(level_name='low', ...)`. Adjusts the exhaust fan speed for low mode.
        5. Medium Supply Fan Speed (Parameter 5): Controlled via `set_fan_speed(level_name='medium', ...)`. Adjusts the supply fan speed for medium mode.
        6. Medium Exhaust Fan Speed (Parameter 6): Controlled via `set_fan_speed(level_name='medium', ...)`. Adjusts the exhaust fan speed for medium mode.
        7. High Supply Fan Speed (Parameter 7): Controlled via `set_fan_speed(level_name='high', ...)`. Adjusts the supply fan speed for high mode.
        8. High Exhaust Fan Speed (Parameter 8): Controlled via `set_fan_speed(level_name='high', ...)`. Adjusts the exhaust fan speed for high mode.
        9. Boost Mode Fan Speed (Parameter 9): Controlled by `set_boost_mode_speed()`. Adjusts the fan speed in boost mode (0-100%).
        10. Filter Replacement Time (Parameter 10): Controlled by `set_filter_replacement_time()`. Sets the number of days until filter replacement notification (90, 120, 150, 180 days).
        11. Humidity Scenario (Parameter 11): Controlled by `set_humidity_scenario()`. Sets the humidity scenario mode (0 for medium, 1 for high).
        12. Sensor Sensitivity (Parameter 12): Controlled by `set_sensor_sensitivity()`. Adjusts the sensitivity of the sensor (0-15).
        13. Humidity Sensor Overrun Time (Parameter 13): Controlled by `set_humidity_scenario_runtime()`. Sets the overrun time for humidity detection (15-60 minutes).
        14. Comfort Temperature (Parameter 14): Controlled by `set_comfort_temperature()`. Adjusts the comfort temperature setting (0.0°C to 30.0°C).
        15. Cooling Season Activation Temperature (Parameter 15): Controlled by `set_cooling_activation_temp()`. Sets the outdoor temperature for cooling season activation (0°C to 30°C).
        16. Minimal Speed of the HRC in Bypass Scenario (Parameter 16): Controlled by set_min_fan_speed_during_bypass(). Adjusts the minimal fan speed of the HRC in the bypass scenario (0-100%).
        17. Regulation Setting for Bypass Fan Speed (Parameter 17): Controlled by set_bypass_fan_speed_regulation(). Adjusts the regulation setting for bypass fan speed (default: 4).
        18. Bypass Fan Speed Setting (Parameter 18): Controlled by set_bypass_fan_speed_setting(). Adjusts the bypass fan speed setting (default: 0).

    Additional Functions:
        - Bypass Control: Includes `open_bypass()`, `close_bypass()`, and `automatic_bypass()` for managing the bypass settings.
        - Predefined Modes: Functions like `set_to_low_mode()`, `set_to_medium_mode()`, `set_to_high_mode()`, and `set_to_auto_mode()` provide convenience for common operations.

    Note: The parameter mappings and ranges are based on the official configuration table provided in the documentation.
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

        Captured commands:
            - Parameter 3 to 28: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003F000F0000003800000000000000A0000000010032
            - Parameter 3 to 27: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003F000F0000003600000000000000A0000000010032
            - Parameter 3 to 26: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003F000F0000003400000000000000A0000000010032
            - Parameter 4 to 40: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000040000F0000005000000000000000A0000000010032
            - Parameter 4 to 26: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000040000F0000003400000000000000A0000000010032
            - Parameter 5 to 44: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000041000F0000005800000000000000C8000000010032
            - Parameter 6 to 50: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000042000F0000006400000014000000C8000000010032
            - Parameter 6 to 58: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000042000F0000007400000014000000C8000000010032
            - Parameter 6 to 60: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000042000F0000007800000014000000C8000000010032
            - Parameter 7 to 73: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000043000F0000009200000000000000C8000000010032
            - Parameter 8 to 79: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 000044000F0000009E00000014000000C8000000010032

        
        :param param: The parameter number (3..8).
        :param speed_percentage: The speed percentage (1..100).
        :return: The hex string payload (without spacing).
        :raises ValueError: if param or speed_percentage are out of range.
        """
        param_suffix = {
            3: "00000000000000A0000000010032",
            4: "00000000000000A0000000010032",
            5: "00000000000000C8000000010032",
            6: "00000014000000C8000000010032",
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

        Default is 0%

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

        Default is 0%

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
        Only predefined values (90, 120, 150, 180) are accepted, with corresponding payloads.

        Captured commands:
        - value 90:  W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003100100000005A00000000000007080000001E002C
        - value 120: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003100100000007800000000000007080000001E002C
        - value 150: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00003100100000009600000000000007080000001E002C
        - value 180: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000310010000000B400000000000007080000001E002C

        default: 180

        :param days: The desired time until filter replacement in days (90, 120, 150, 180).
        :return: The command string to set the filter replacement time.
        :raises ValueError: if days are not in the predefined set of values.
        """
        # Mapping of allowed days to their corresponding payload values.
        payload_map = {
            90:  "00003100100000005A00000000000007080000001E002C",
            120: "00003100100000007800000000000007080000001E002C",
            150: "00003100100000009600000000000007080000001E002C",
            180: "0000310010000000B400000000000007080000001E002C",
        }

        if days not in payload_map:
            raise ValueError("Days must be one of the following: 90, 120, 150, 180.")

        # Retrieve the corresponding payload for the given days.
        payload = payload_map[days]
        
        # Build the complete message.
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
        value 6: 		W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00005200010000003C00000000000000FA000000010032
        value 15:		W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00005200010000009600000000000000FA000000010032
        value 5: 		W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00005200010000003200000000000000FA000000010032

        :param sensitivity: The desired sensor sensitivity (0..15).
        :return: The command string to set the sensor sensitivity.
        :raises ValueError: if sensitivity is out of range.
        """
        if not (0 <= sensitivity <= 15):
            raise ValueError("Sensor sensitivity must be between 0 and 15.")

        # Calculate the ParamID for Parameter 12 (fixed as 0x52).
        param_id = 0x52

        # Multiply the sensitivity value by 12 to match observed encoding (e.g., 5 -> 0x3C).
        sensitivity_hex = f"{sensitivity * 12:02X}"

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

    def set_humidity_scenario(self, mode: int) -> str:
        """
        Generate the command payload to set the humidity scenario (Parameter 11).

        This function controls the humidity scenario setting. The value can be:
        - 0: Midden (Medium)
        - 1: Hoog (High)

        Captured commands:
        - Waarde 1: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00004E0000000000010000000000000001000000010000
        - Waarde 0: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00004E0000000000000000000000000001000000010000

        :param mode: The desired humidity scenario mode (0 or 1).
        :return: The command string to set the humidity scenario.
        :raises ValueError: if mode is not 0 or 1.
        """
        if mode not in (0, 1):
            raise ValueError("Humidity scenario mode must be 0 (Midden) or 1 (Hoog).")

        if mode == 0:
            msg = f"W --- {self.remote} {self.wtw} --:------ 2411 023 00004E0000000000000000000000000001000000010000"
        
        if mode == 1:
            msg = f"W --- {self.remote} {self.wtw} --:------ 2411 023 00004E0000000000010000000000000001000000010000"

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

        Captured commands:
        - Value 20.1: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000007DA0000000000000BB8000000010001
        - Value 20.5: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008020000000000000BB8000000010001
        - Value 22.3: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008B60000000000000BB8000000010001
        - Value 20.1: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000007DA0000000000000BB8000000010001
        - Value 20.2: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000007E40000000000000BB8000000010001
        - Value 21.0: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008340000000000000BB8000000010001
        - Value 21.2: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000750092000008480000000000000BB8000000010001

        :param temperature: The desired comfort temperature in °C (0.0..30.0).
        :return: The command string to set the comfort temperature.
        :raises ValueError: if temperature is out of range.
        """
        if not (0.0 <= temperature <= 30.0):
            raise ValueError("Comfort temperature must be between 0.0 and 30.0°C.")

        # Convert the temperature to the hexadecimal value used in the payload
        temperature_hex = int(temperature * 100)

        # Format the temperature as a 4-character uppercase hex string
        temperature_encoded = f"{temperature_hex:04X}"

        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 00007500920000{temperature_encoded}0000000000000BB8000000010001"
        )

        return [msg]

    def set_cooling_activation_temp(self, temperature_celsius: int) -> str:
        """
        Set the outdoor temperature for activation of the cooling season in the Orcon WTW unit.

        Captured Commands:
        - Temperature 0°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000000000000000000003C000000010001
        - Temperature 1°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000002000000000000003C000000010001
        - Temperature 2°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000004000000000000003C000000010001
        - Temperature 14°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F0000001C000000000000003C000000010001
        - Temperature 15°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F0000001E000000000000003C000000010001
        - Temperature 16°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000020000000000000003C000000010001
        - Temperature 17°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000022000000000000003C000000010001
        - Temperature 20°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000028000000000000003C000000010001
        - Temperature 24°C: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000A1000F00000030000000000000003C000000010001

        Default: 15°C

        Args:
            temperature_celsius (int): The desired activation temperature in Celsius (e.g., 14, 15, 16, etc.).

        Returns:
            str: The command string to send to the WTW unit.
        """
        if not (0 <= temperature_celsius <= 30):
            raise ValueError("Activation temperature must be between 0 and 30 degrees Celsius.")

        # Calculate the ParamID for Parameter 15
        param_id = 0xA1

        # Multiply the temperature by 2 to get the hex representation.
        temperature_hex = f"{temperature_celsius * 2:02X}"

        # Build the prefix based on observations.
        prefix = f"0000{param_id:02X}000F000000{temperature_hex}"

        # Fixed suffix for Parameter 15 based on patterns in data.
        suffix = "000000000000003C000000010001"

        # Combine prefix + suffix into a single hex string payload.
        payload = prefix + suffix
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )

        return [msg]

    def set_min_fan_speed_during_bypass(self, speed_percentage: int) -> str:
        """
        Build the hex payload for setting the minimum fan speed during bypass.
        This is for parameter 16, based on observed radio traffic.

        Radio traffic for parameter 16:
            - Value 28: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000011800000000000003E8000000010032
            - Value 32: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000014000000000000003E8000000010032
            - Value 35: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000015E00000000000003E8000000010032
            - Value 100: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000790011000003E800000000000003E8000000010032
            - Value 0: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000000000000000000003E8000000010032
            - Value 4: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000002800000000000003E8000000010032
            - Value 8: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000005000000000000003E8000000010032
            - Value 12: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000007800000000000003E8000000010032
            - Value 16: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000790011000000A000000000000003E8000000010032
            - Value 10: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000003200000000000003E8000000010032
            - Value 20: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000790011000000C800000000000003E8000000010032
            - Value 60: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000025800000000000003E8000000010032
            - Value 70: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000790011000002BC00000000000003E8000000010032
            - Value 80: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 00007900110000032000000000000003E8000000010032
            - Value 90: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000790011000003E800000000000003E8000000010032

        :param speed_percentage: The speed percentage (0..100).
        :return: The hex string payload (without spacing).
        :raises ValueError: if speed_percentage is out of range.
        """
        if not (0 <= speed_percentage <= 100):
            raise ValueError("Speed percentage for minimum fan speed during bypass must be between 0 and 100.")

        # Calculate the hex value for the speed percentage
        hex_speed = f"{speed_percentage * 10:04X}"  # Convert to a 4-character zero-padded hex string

        # Build the payload string
        payload = f"00007900110000{hex_speed}00000000000003E8000000010032"

        # Build the complete message
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )

        return [msg]

    def set_bypass_fan_speed_regulation(self, setting: int) -> str:
        """
        Adjust the regulation setting for bypass fan speed.

        Parameter 17 corresponds to the bypass fan speed regulation setting.

        Captured traffic:
            3: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000E70000000000030000000300000005000000010000
            4: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000E70000000000040000000300000005000000010000

        :param setting: The desired regulation setting (3 for medium, 4 for high).
        :return: The command string for setting the bypass fan speed regulation.
        :raises ValueError: If the provided setting is not 3 or 4.
        """
        if setting not in (3, 4):
            raise ValueError("Regulation setting for parameter 17 must be 3 (medium) or 4 (high).")

        if setting == 3:
            payload = "0000E70000000000030000000300000005000000010000"

        if setting == 4:
            payload = "0000E70000000000040000000300000005000000010000"

        # Construct the full message
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )

        return [msg]
    
    def set_bypass_fan_speed_setting(self, setting: int) -> str:
        """
        Adjust the bypass fan speed setting.

        Parameter 18 corresponds to the bypass fan speed setting.

        Captured traffic:

        1: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000E80000000000010000000000000001000000010000
        0: W --- 37:XXXXX 32:YYYYY --:------ 2411 023 0000E80000000000000000000000000001000000010000

        :param setting: The desired setting (0 to follow parameter 16, 1 to follow parameter 17).
        :return: The command string for setting the bypass fan speed.
        :raises ValueError: If the provided setting is not 0 or 1.
        """
        if setting not in (0, 1):
            raise ValueError("Bypass fan speed setting for parameter 18 must be 0 or 1.")
        
        if setting == 0:
            payload = "0000E80000000000000000000000000001000000010000"

        if setting == 1:
            payload = "0000E80000000000010000000000000001000000010000"
        
        # Construct the full message
        msg = (
            f"W --- {self.remote} {self.wtw} --:------ "
            f"2411 023 {payload}"
        )

        return [msg]
