#include "voltage.h"

const char *voltage_string[] = {
	[VOLTAGE_LOW] = "Low",
	[VOLTAGE_MEDIUM] = "Medium",
	[VOLTAGE_HIGH] = "High",
};

const char *voltage_to_string(Voltage voltage)
{
	return voltage_string[voltage];
}
