#ifndef VOLTAGE_H
#define VOLTAGE_H

//Voltage categories
enum Voltage {
	VOLTAGE_LOW,
	VOLTAGE_MEDIUM,
	VOLTAGE_HIGH,
};

// Converts voltage to string
const char *voltage_to_string(Voltage voltage);

#endif
