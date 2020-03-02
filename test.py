import time

# Import the ADS1x15 module.
import Adafruit_ADS1x15

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

print('Reading ADS1x15 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('                    | {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
print('-' * 57)
# Main loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = (adc.read_adc(i, gain=GAIN))/10000
        now = time.strftime('%d/%m/%Y %H:%M:%S')

    # Print the ADC values.
    print(now + ' | {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    # Pause for 1 hour.
    time.sleep(.3600)
