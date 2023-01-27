# # 
# Firmware adapted from https://github.com/RequestForCoffee/scd30
import datetime
from datetime import timedelta
import logging
import smbus2
import struct
import time

# to_s16 = lambda x: (x + 2**15) % 2**16 - 2**15
# to_u16 = lambda x: x % 2**16

SCD30_I2C_ADDR = 0x61

GET_FIRMWARE_VER                  =0xD100
CONTINUOUS_MEASUREMENT            =0x0010
SET_MEASUREMENT_INTERVAL          =0x4600
GET_DATA_READY                    =0x0202
READ_MEASUREMENT                  =0x0300
STOP_MEASUREMENT                  =0x0104
AUTOMATIC_SELF_CALIBRATION        =0x5306
SET_FORCED_RECALIBRATION_FACTOR   =0x5204
SET_TEMPERATURE_OFFSET            =0x5403
SET_ALTITUDE_COMPENSATION         =0x5102
READ_SERIALNBR                    =0xD033
SET_TEMP_OFFSET                   =0x5403
SOFT_RESET                        =0xD304
POLYNOMIAL                        =0x31


class SCD30:

    def __init__(self, i2c_dev,debugIn):
        
        self.i2c_addr = SCD30_I2C_ADDR
        self.i2c      = i2c_dev
        self.debug    =  debugIn

    def initiate(self,retriesIn):
        ready = None
        
        while ready is None and retriesIn:
            try:
                ready = self.get_data_ready()

            except OSError:
                pass
            time.sleep(1)
            retriesIn -= 1

        if not retriesIn:
            time.sleep(1)
            return False
        else:
            self.get_firmware_version()
            self.set_measurement_interval(5)
            self.set_auto_self_calibration(active=False)
            self.start_periodic_measurement()
            time.sleep(1)
            return True 
    
    def read(self):
        if self.get_data_ready():
            measurement = self.read_measurement()
            if measurement is not None:
                co2, temp, rh = measurement
                dateTime = datetime.datetime.now() 
                print("CO2: {:.2f}ppm, temp: {:.2f}'C, rh: {:.2f}%".format(co2,temp,rh))
                time.sleep(1)

                return [dateTime,co2,temp,rh];
            else:
                time.sleep(1)
                return [];
                print("SCD30 Measurments not read")    
        else:
            time.sleep(1)
            print("SCD30 Not Ready")
            return;


        

    def get_firmware_version(self):
        """Reads the firmware version from the sensor.

        Returns:
            two-byte integer version number
        """
        return self.job_word_or_none(self.job_send_command(GET_FIRMWARE_VER))

    def get_data_ready(self):
        return self.job_word_or_none(self.job_send_command(GET_DATA_READY))

    def start_periodic_measurement(self, ambient_pressure: int = 0):
        """Starts periodic measurement of CO2 concentration, humidity and temp.

        Parameters:
            ambient_pressure (optional): external pressure reading in millibars.

        The enable status of periodic measurement is stored in non-volatile
        memory onboard the sensor module and will persist after shutdown.

        ambient_pressure may be set to either 0 to disable ambient pressure
        compensation, or between [700; 1400] mBar.
        """
        if ambient_pressure and not 700 <= ambient_pressure <= 1400:

            print("Ambient pressure must be set to either 0 or in "
                             "the range [700; 1400] mBar")
            time.sleep(1000)


        self.job_send_command(CONTINUOUS_MEASUREMENT, num_response_words=0,
                           arguments=[ambient_pressure])

    def stop_periodic_measurement(self):
        """Stops periodic measurement of CO2 concentration, humidity and temp.

        The enable status of periodic measurement is stored in non-volatile
        memory onboard the sensor module and will persist after shutdown.
        """
        self.job_send_command(STOP_MEASUREMENT, num_response_words=0)

    def get_measurement_interval(self):
        """Gets the interval used for periodic measurements.

        Returns:
            measurement interval in seconds or None.
        """
        interval = self.job_word_or_none(
            self.job_send_command(SET_MEASUREMENT_INTERVAL, 1))

        if interval is None or not 2 <= interval <= 1800:
            print("Failed to read measurement interval, received: " +
                         str(self.job_pretty_hex(interval)))

        return interval

    def set_measurement_interval(self, interval=2):
        """Sets the interval used for periodic measurements.

        Parameters:
            interval: the interval in seconds within the range [2; 1800].

        The interval setting is stored in non-volatile memory and persists
        after power-off.
        """
        if not 2 <= interval <= 1800:
            print("Interval must be in the range [2; 1800] (sec)")
            time.sleep(10)

        self.job_send_command(SET_MEASUREMENT_INTERVAL, 1, [interval])

    def read_measurement(self):

        """Reads out a CO2, temperature and humidity measurement.

        Must only be called if a measurement is available for reading, i.e.
        get_data_ready() returned 1.

        Returns:
            tuple of measurement values (CO2 ppm, Temp 'C, RH %) or None.
        """

        data = self.job_send_command(READ_MEASUREMENT, num_response_words=6)

        if data is None or len(data) != 6:
            print("Failed to read measurement, received: " +
                          self.job_pretty_hex(data))
            return None

        co2_ppm      = self.job_interpret_as_float((data[0] << 16) | data[1])
        temp_celsius = self.job_interpret_as_float((data[2] << 16) | data[3])
        rh_percent   = self.job_interpret_as_float((data[4] << 16) | data[5])

        return (co2_ppm, temp_celsius, rh_percent)

    def set_auto_self_calibration(self, active: bool):
        """(De-)activates the automatic self-calibration feature.

        Parameters:
            active: True to enable, False to disable.

        The setting is persisted in non-volatile memory.
        """
        arg = 1 if active else 0
        self.job_send_command(AUTOMATIC_SELF_CALIBRATION,
                     num_response_words=0, arguments=[arg])

    def get_auto_self_calibration_active(self):
        """Gets the automatic self-calibration feature status.

        Returns:
            1 if ASC is active, 0 if inactive, or None upon error.
        """
        return self.job_word_or_none(
            self.job_send_command(AUTOMATIC_SELF_CALIBRATION))

    def get_temperature_offset(self):
        """Gets the currently active temperature offset.

        The temperature offset is used to compensate for reading bias caused by
        heat generated by nearby electrical components or the SCD30 itself.

        See the documentation of set_temperature_offset for more details on
        calculating the offset value correctly.

        The temperature offset is stored in non-volatile memory and persists
        across shutdowns.

        Returns:
            Temperature offset floating-point value in degrees Celsius.
        """
        offset_ticks = self.job_word_or_none(self.job_send_command(0x5403))
        if offset_ticks is None:
            return None
        return offset_ticks / 100.0

    def set_temperature_offset(self, offset: float):
        """Sets a new temperature offset.

        The correct temperature offset will vary depending on the installation
        of the sensor as well as its configuration; different measurement
        intervals will result in different power draw, and thus, different
        amounts of electrical heating.

        To compute the offset value for any fixed configuration:
            1. Install and configure the sensor as needed.
            2. Start continuous measurement and let it run for at least 10
               minutes or until a stable temperature equilibrium is reached.
            3. Get the previous temperature offset value T_offset_old from
               the SCD30 using get_temperature_offset.
            4. Get a temperature reading T_measured from the SCD30 using
               read_measurement.
            5. Measure the ambient temperature T_ambient using a *different*
               sensor, away from the immediate proximity of the SCD30.
            6. Compute the new offset to set as follows:
               T_offset_new = (T_measured + T_offset_old) - T_ambient

        After setting a new value, allow the sensor readings to stabilize,
        which will happen slowly and gradually.

        For more details, see the documentation on the project page.

        Arguments:
            offset: temperature offset floating-point value in degrees Celsius.
        """
        offset_ticks = int(offset * 100)
        return self.job_send_command(SET_TEMPERATURE_OFFSET, 0, [offset_ticks])

    def soft_reset(self):
        """Resets the sensor without the need to disconnect power.

        This restarts the onboard system controller and forces the sensor
        back to its power-up state.
        """
        self.job_send_command(SOFT_RESET, num_response_words=0)


    ### All The JOBS NEEDED FOR SCD30 I2C  
    def job_check_word(self, word):
        """Checks weather the data added is actually 2 bytes or less.
         If not it throws an error.
        """
        if not 0 <= word <= 0xFFFF:
            print(" Not withing the confines of 2 bytes:" + str(word ))
            
    def job_send_command(self, command: int, num_response_words: int = 1,
                      arguments: list = []):
        
        """Makes the I2C command, Has the flexibilty to take in arguments if 
        needed. The function also reads the response. Writes and in some cases 
        reads to and from the sensor. 
        
        Parameters:
            command: Two-byte command which is typically the register address
                    E.g. 0x0010.
            num_response_words: two-byte words meant to be read.
            arguments: For some commands, an argument is needed. This is typically  
            to tune the SCD30 or to change its reading frequencies.
            This is a list of two-byte words.

        Returns:
            list of num_response_words two-byte int values from the sensor.
            Eg: Firmware version
        """
        # Check to see if the command is valid 
        self.job_check_word(command)
		
        if(self.debug):
            print("Executing command " + str(self.job_pretty_hex(command)) + "with "
                      "arguments:" + str(self.job_pretty_hex(arguments)))

        """
        # Each Messege with no arguments which is written should be 
        # of the following order
        # Command: with 2 bytes
        
        # Each Messege with arguments which is written should be 
        # of the following order
        # Command:  with 2 bytes
        # [Argument: with 2 bytes  
        # CRC Check byte (cyclic_redundancy_check)] * number of arguments 
        """

        raw_message = list(command.to_bytes(2, "big"))
        
        # Nothing happens if there are no arguments
        for argument in arguments:
            self.job_check_word(argument)
            raw_message.extend(argument.to_bytes(2, "big"))
            raw_message.append(self.job_crc8(argument))
		
        if(self.debug):
        	print("Sending raw I2C data block: "+ str(self.job_pretty_hex(raw_message)))

        # self.i2c.write_i2c_block_data(self._i2c_addr, command, arguments)

        # Create an i2c messege instance to be used with i2c_rdwr()
        write_txn = smbus2.i2c_msg.write(SCD30_I2C_ADDR, raw_message)
        
        # Writing the I2C Messege 
        self.i2c.i2c_rdwr(write_txn)

       
        # Waiting for the reply from the sensor
        # The interface description suggests a >3ms delay between writes and
        # reads for most commands.
        time.sleep(timedelta(milliseconds=5).total_seconds())

        # If a reply is not expected exit
        if num_response_words == 0:
            return []

        # Create an i2c messege instance to be used with i2c_rdwr()
        # 3x since  word is 2 bytes and each word gives a crc 
        # Sorting out the read byte format 
        read_txn = smbus2.i2c_msg.read(self.i2c_addr, num_response_words * 3)
        
        # reading the I2C Messege / Adding it to read_txn
        self.i2c.i2c_rdwr(read_txn)

        # raw_response = self._i2c.read_i2c_block_data(
        #    self._i2c_addr, command, 3 * num_response_words)

        raw_response = list(read_txn)
		
        if(self.debug):
        	print("Received raw I2C response: " + str(self.job_pretty_hex(raw_response)))

        if len(raw_response) != 3 * num_response_words:
            print("Wrong response length: " + str(len(raw_response)) 
                   + "expected: " + str(3*num_response_words)
                  )

        # Data is returned as a sequence of num_response_words 2-byte words
        # (big-endian), each with a CRC-8 checksum:
        # [MSB0, LSB0, CRC0, MSB1, LSB1, CRC1, ...]

        response = []

        for i in range(num_response_words):
            # Looking at each word seperately 
            # word_with_crc contains [MSB, LSB, CRC] for the i-th response word
            word_with_crc = raw_response[3 * i: 3 * i + 3]
            word = int.from_bytes(word_with_crc[:2], "big")
            response_crc = word_with_crc[2]
            computed_crc = self.job_crc8(word)
            if (response_crc != computed_crc):
                print(
                    "CRC verification for word " + str(self.job_pretty_hex(word)) +
                    "failed: received " + str(self.job_pretty_hex(response_crc)) +
                    "computed " +str(self.job_pretty_hex(computed_crc)))
                return None
            response.append(word)
		
        if(self.debug):
        	print("CRC-verified response: " + str(self.job_pretty_hex(response)))
        
        return response


    def job_pretty_hex(self, data):
        """Formats an I2C message in an easily readable format.

        Parameters:
            data: either None, int, or a list of ints.

        Returns:
            a string '<none>' or hex-formatted data (singular or list).
        """
        if data is None:
            return "<none>"
        if type(data) is int:
            data = [data]
        if len(data) == 0:
            return "<none>"

        if len(data) == 1:
            value = "{:02x}".format(data[0])
            if len(value) % 2:
                value = "0" + value
            return "0x" + value
        return "[" + ", ".join("0x{:02x}".format(byte) for byte in data) + "]"


    def job_word_or_none(self, response: list):
        """Unpacks an I2C response as either a single 2-byte word or None.

        Parameters:
            response: None or a single-value list.

        Returns:
            None or the single value inside 'response'.
        """
        return next(iter(response or []), None)

    def job_crc8(self, word: int):
        """Computes the CRC-8 checksum as per the SCD30 interface description.

        Parameters:
            word: two-byte integer word value to compute the checksum over.

        Returns:
            single-byte integer CRC-8 checksum.

        Polynomial: x^8 + x^5 + x^4 + 1 (0x31, MSB)
        Initialization: 0xFF

        Algorithm adapted from:
        https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks

        """
        self.job_check_word(word)
        polynomial = POLYNOMIAL
        rem = 0xFF
        word_bytes = word.to_bytes(2, "big")
        for byte in word_bytes:
            rem ^= byte
            for _ in range(8):
                if rem & 0x80:
                    rem = (rem << 1) ^ polynomial
                else:
                    rem = rem << 1
                rem &= 0xFF

        return rem

    def job_interpret_as_float(self,integer: int):
        return struct.unpack('!f', struct.pack('!I', integer))[0]