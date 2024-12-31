import logging

logger = logging.getLogger(__name__)


class OrconRamsesRFCommand:
    """
    This class can generate commands to set fan speeds (1 to 100%) 
    for parameters 3 through 8 on an Orcon HRC 400 ventilation unit, 
    which uses the Ramses II protocol.
    
    It demonstrates how to build the 'Write' command payload 
    based on log observations. 
    """

    def __init__(self, remote_address, wtw_address, capacity_in_m3_per_hour=400):
        """
        :param remote_address: The address of the remote (e.g. "37:090513")
        :param wtw_address: The address of the WTW unit (e.g. "32:155065")
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
    