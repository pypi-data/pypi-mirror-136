# ================================= #
# Module: ElectronicsCalculator.py  #
# Author: Mino Girimonti            #
# License: GPL v3.0                 #
# ================================= #
"""This module provides methods to perform common electronics calculations."""

import math

# ========= #
# CONSTANTS #
# ========= #
SPEED_OF_LIGHT = 300000000  # Meters per second
PI = math.pi


# ========= #
# OHM'S LAW #
# ========= #
def power_er(voltage, resistance):
    """
    Calculates power based on voltage and resistance values using Ohm's Law.

    Inputs:
    *   voltage: V (Volts)
    *   resistance: R (Ohms)

    Output:
    *   power: P (Watts)
    """
    retval = 0

    try:
        retval = pow(voltage, 2) / resistance
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Resistance cannot be 0")

    return retval


def power_ie(current, voltage):
    """
    Calculates power based on current and voltage values using Ohm's Law.

    Inputs:
    *   current: I (Amperes)
    *   voltage: V (Volts)

    Output:
    *   power: P (Watts)
    """
    retval = 0

    try:
        retval = (current * voltage) / 1    # Divide by 1 to force TypeError if nun-numeric parameters passed in
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def power_ir(current, resistance):
    """
    Calculates power based on current and resistance values using Ohm's Law. P

    Inputs:
        current: I (Amperes)
        resistance: R (Ohms)

    Output:
        power: P (Watts)
    """
    retval = 0

    try:
        retval = pow(current, 2) * resistance
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def current_pe(power, voltage):
    """
    Calculates current based on power and voltage values using Ohm's Law.

    Inputs:
        power: P (Watts)
        voltage: V (Volts)

    Output:
        current: I (Amperes)
    """
    retval = 0

    try:
        retval = power / voltage
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Voltage cannot be 0")

    return retval


def current_pr(power, resistance):
    """
    Calculates current based on power and resistance values using Ohm's Law.

    Inputs:
    *   power: P (Watts)
    *   resistance: R (Ohms)

    Output:
    *   current: I (Amperes)
    """
    retval = 0

    try:
        retval = math.sqrt(power / resistance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Resistance cannot be 0")

    return retval


def current_er(voltage, resistance):
    """
    Calculates current based on voltage and resistance values using Ohm's Law.

    Inputs:
    *   voltage: V (Volts)
    *   resistance: R (Ohms)

    Output:
    *   current: I (Amperes)
    """
    retval = 0

    try:
        retval = voltage / resistance
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Resistance cannot be 0")

    return retval


def voltage_pi(power, current):
    """
    Calculates voltage based on power and current values using Ohm's Law.

    Inputs:
    *   power: P (Watts)
    *   current: I (Amperes)

    Output:
    *   voltage: V (Volts)
    """
    retval = 0

    try:
        retval = power / current
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Current cannot be 0")

    return retval


def voltage_pr(power, resistance):
    """
    Calculates voltage based on power and resistance values using Ohm's Law.

    Inputs:
    *   power: P (Watts)
    *   resistance: R (Ohms)

    Output:
    *   voltage: V (Volts)
    """
    retval = 0

    try:
        retval = math.sqrt(power * resistance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def voltage_ir(current, resistance):
    """
    Calculates voltage based on current and resistance values using Ohm's Law.

    Inputs:
    *   current: I (Amperes)
    *   resistance: R (Ohms)

    Output:
    *   voltage: V (Volts)
    """
    retval = 0

    try:
        retval = (current * resistance) / 1     # Force TypeError if non-numerics are passed in
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def resistance_pe(power, voltage):
    """
    Calculates resistance based on power and voltage values using Ohm's Law.

    Inputs:
    *   power: P (Watts)
    *   voltage: V (Volts)

    Output:
    *   resistance: R (Ohms)
    """
    retval = 0

    try:
        retval = pow(voltage, 2) / power
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Power cannot be 0")

    return retval


def resistance_pi(power, current):
    """
    Calculates resistance based on power and current values using Ohm's Law.

    Inputs:
    *   power: P (Watts)
    *   current: I (Amperes)

    Output:
    *   resistance: R (Ohms)
    """
    retval = 0

    try:
        retval = power / pow(current, 2)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Current cannot be 0")

    return retval


def resistance_ie(current, voltage):
    """
    Calculates resistance based on current and voltage values using Ohm's Law.

    Inputs:
    *   current: I (Amperes)
    *   voltage: V (Volts)

    Output:
    *   resistance: R (Ohms)
    """
    retval = 0

    try:
        retval = voltage / current
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Current cannot be 0")

    return retval


def voltage_divider_r(voltage_in, resistance_1, resistance_2):
    """
    Calculates output voltage when two resistors are used as a voltage divider. The output voltage will always
    be lower than the input voltage.

    Inputs:
    *   voltage_in: Vin (Volts)
    *   resistance_1: R1 (Ohms)
    *   resistance_2: R2 (Ohms)

    Output:
    *   voltage_out: Vout (Volts)
    """
    retval = 0

    try:
        retval = voltage_in * (resistance_2 / (resistance_1 + resistance_2))
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("At least one of the Resistance values needs to be something other than 0")

    return retval


# ================================================================================================================= #
#                                                   DIRECT CURRENT                                                  #
# ================================================================================================================= #

# =============== #
# SERIES CIRCUITS #
# =============== #
def total_series_current(currents: tuple):
    """
    Takes a tuple of current measurements in a series circuit and returns the total current.

    Inputs:
    *   currents: I (Amperes)

    Output:
    *   total_current: I (Amperes)
    """
    retval = 0
    total = 0
    count = 1

    try:
        for item in currents:
            total += item
            average = total / count

            if item != average:
                raise ValueError

            count += 1

        retval = currents[0]
    except IndexError:
        raise IndexError("At least one input is required")
    except ValueError:
        raise ValueError("All current measurements in a series circuit should be identical.")
    except TypeError:
        raise TypeError("Function is expecting a tuple of numeric values")

    return retval


def total_series_resistance(resistances: tuple):
    """
    Takes a tuple of resistance measurements in a series circuit and returns the total resistance.

    Inputs:
    *   resistances: R (Ohms)

    Output:
    *   total_resistance: R (Ohms)
    """
    retval = 0

    try:
        if len(resistances) == 0:
            raise ValueError

        retval = _sums(resistances)
    except ValueError:
        raise ValueError("All parameters must be numeric")
    except TypeError:
        raise TypeError("Function is expecting a tuple of numeric values")

    return retval


def total_series_voltage(voltages: tuple):
    """
    Takes a tuple of voltage measurements in a series circuit and returns the total voltage.

    Inputs:
    *   voltages: V (Volts)

    Output:
    *   total_voltage: V (Volts)
    """
    retval = 0

    try:
        if len(voltages) == 0:
            raise ValueError

        retval = _sums(voltages)
    except ValueError:
        raise ValueError("All parameters must be numeric")
    except TypeError:
        raise TypeError("Function is expecting a tuple of numeric values")

    return retval


def total_series_capacitance(capacitances: tuple):
    """
    Takes a tuple of capacitance measurements in a series circuit and returns the total capacitance.

    Inputs:
    *   capacitances: C (Farads)

    Output:
    *   total_capacitance: C (Farads)
    """
    retval = 0

    try:
        if len(capacitances) == 0:
            raise ValueError

        retval = _inverse_sums(capacitances)
    except ValueError:
        raise ValueError("At least one parameter must be entered")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


def total_series_inductance(inductances: tuple):
    """
    Takes a tuple of inductance measurements in a series circuit and returns the total inductance.

    Inputs:
    *   inductances: L (Henries)

    Output:
    *   total_inductance: L (Henries)
    """
    retval = 0

    try:
        if len(inductances) == 0:
            raise ValueError

        retval = _sums(inductances)
    except ValueError:
        raise ValueError("At least one parameter must be entered")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")

    return retval


# ================= #
# PARALLEL CIRCUITS #
# ================= #
def total_parallel_current(currents: tuple):
    """
    Takes a tuple of current measurements in a parallel circuit and returns the total current.

    Inputs:
    *   currents: I (Amperes)

    Output:
    *   total_current: I (Amperes)
    """

    retval = 0

    try:
        if len(currents) == 0:
            raise ValueError

        retval = _sums(currents)
    except ValueError:
        raise ValueError("At least one parameter must be entered")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")

    return retval


def total_parallel_resistance(resistances: tuple):
    """
    Takes a tuple of resistance measurements in a parallel circuit and returns the total resistance.

    Inputs:
    *   resistances: R (Ohms)

    Output:
    *   total_resistance: R (Ohms)
    """
    retval = 0

    try:
        if len(resistances) == 0:
            raise ValueError

        retval = _inverse_sums(resistances)
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


def total_parallel_voltage(voltages: tuple):
    """
    Takes a tuple of voltage measurements in a parallel circuit and returns the total voltage.

    Inputs:
    *   voltages: V (Volts)

    Output:
    *   total_voltage: V (Volts)
    """
    retval = 0
    total = 0
    count = 1

    try:
        for item in voltages:
            total += item  # will force a TypeError for any non-numerics in the tuple
            average = total / count

            if item != average:  # All individual numbers should equal the average if they are identical
                raise ValueError

            count += 1

        retval = voltages[0]
    except IndexError:
        raise IndexError("At least one value is required")
    except ValueError:
        raise ValueError("All voltage measurements in a parallel circuit should be identical")
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def total_parallel_capacitance(capacitances: tuple):
    """
    Takes a tuple of capacitance measurements in a parallel circuit and returns the total capacitance.

    Inputs:
    *   capacitances: C (Farads)

    Output:
    *   total_capacitance: C (Farads)
    """
    retval = 0

    try:
        if len(capacitances) == 0:
            raise ValueError

        retval = _sums(capacitances)
    except ValueError:
        raise ValueError("At least one parameter is required")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")

    return retval


def total_parallel_inductance(inductances: tuple):
    """
    Takes a tuple of inductance measurements in a parallel circuit and returns the total inductance.

    Inputs:
    *   inductances: L (Henries)

    Output:
    *   total_inductance: L (Henries)
    """
    retval = 0

    try:
        if len(inductances) == 0:
            raise ValueError

        retval = _inverse_sums(inductances)
    except ValueError:
        raise ValueError("At least one parameter is required")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


# ================================================================================================================= #
#                                               ALTERNATING CURRENT                                                 #
# ================================================================================================================= #
# ========= #
# FREQUENCY #
# ========= #
def frequency_cxc(capacitance, capacitive_reactance):
    """
    Calculates frequency when capacitance and capacitive reactance are known.

    Inputs:
    *   capacitance: C (Farads)
    *   capacitive_reactance: Xc (Ohms)

    Output:
    *   frequency: f (Hertz)
    """
    retval = 0

    try:
        retval = _inverse_tau(capacitance, capacitive_reactance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


def frequency_lxl(inductance, inductive_reactance):
    """
    Calculates frequency when inductance and inductive reactance are known.

    Inputs:
    *   inductance: L (Henries)
    *   inductive_reactance: Xl (Ohms)

    Output:
    *   frequency: f (Hertz)
    """
    retval = 0

    try:
        retval = inductive_reactance / (2 * PI * inductance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Inductance cannot be 0")

    return retval


def frequency_wl(wavelength):
    """
    Calculates frequency when wavelength is known.

    Inputs:
    *   wavelength: w (Meters)

    Output:
    *   frequency: f (Hertz)
    """
    retval = 0

    try:
        retval = SPEED_OF_LIGHT / wavelength
    except TypeError:
        raise TypeError("The parameter you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Wavelength cannot be 0")

    return retval


def wavelength(frequency):
    """
    Calculates wavelength when frequency is known.

    Inputs:
    *   frequency: f (Hertz)

    Output:
    *   wavelength: w (Meters)
    """
    retval = 0

    try:
        retval = SPEED_OF_LIGHT / frequency
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Frequency cannot be 0")

    return retval


def antenna_length_qw(frequency):
    """
    Calculates optimal quarter wave antenna length to receive input frequency. This is useful when
    designing dipole radio antennae.

    Inputs:
    *   frequency: f (Hertz)

    Output:
    *   quarter_wavelength: w (Meters)
    """
    retval = 0

    try:
        wl = wavelength(frequency)
        retval = wl / 4.0
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Frequency cannot be 0")

    return retval


# =========== #
# CAPACITANCE #
# =========== #
def capacitance_fxc(frequency, capacitive_reactance):
    """
    Calculates capacitance when frequency and capacitive reactance are known.

    Inputs:
    *   frequency: f (Hertz)
    *   capacitive_reactance: Xc (Ohms)

    Output:
    *   capacitance: C (Farads)
    """
    retval = 0

    try:
        retval = _inverse_tau(frequency, capacitive_reactance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


# ========== #
# INDUCTANCE #
# ========== #
def inductance_fxl(frequency, inductive_reactance):
    """
    Calculates inductance when frequency and inductive reactance are known.

    Inputs:
    *   frequency: f (Hertz)
    *   inductive_reactance: Xl (Ohms)

    Output:
    *   inductance: L (Henries)
    """
    retval = 0

    try:
        retval = inductive_reactance / (2 * PI * frequency)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Frequency cannot be 0")
    return retval


def back_emf(inductance, current_t1, current_t2, time):
    """
    Calculates back EMF when current stops flowing in an inductor. Large voltages tend to get produced
    which can damage components unless sufficient protective diodes are used in the circuits.

    Inputs:
    *   inductance: L (Henries)
    *   current_t1: It1 (Amperes) - Current at T1
    *   current_t2: It2 (Amperes) - Current at T2
    *   time: s (Seconds) - Elapsed time between T1 and T2

    Output:
    *   back_emf: V (Volts)
    """
    retval = 0

    try:
        retval = -inductance * ((current_t2 - current_t1) / time)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Time cannot be 0")

    return retval


# ========= #
# REACTANCE #
# ========= #
def reactance_inductive_fl(frequency, inductance):
    """
    Calculates inductive reactance when frequency and inductance are known.

    Inputs:
    *   frequency: f (Hertz)
    *   inductance: L (Henries)

    Output:
    *   inductive_reactance: Xl (Ohms)
    """
    retval = 0

    try:
        retval = _tau(frequency, inductance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def reactance_capacitive_fc(frequency, capacitance):
    """
    Calculates capacitive reactance when frequency and capacitance are known.

    Inputs:
    *   frequency: f (Hertz)
    *   capacitance: C (Farads)

    Output:
    *   capacitive_reactance: Xc (Ohms)
    """
    retval = 0

    try:
        retval = _inverse_tau(frequency, capacitance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


def reactance_capacitive_zr(impedance, resistance):
    """
    Calculates capacitive reactance when impedance and resistance are known.

    Inputs:
    *   impedance: Z (Ohms)
    *   resistance: R (Ohms)

    Output:
    *   capacitive_reactance: Xc (Ohms)
    """
    retval = 0

    try:
        retval = math.sqrt(pow(impedance, 2) - pow(resistance, 2))
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


# =================== #
# VOLTAGE (Sine wave) #
# =================== #
def voltage_rms_from_peak(peak_voltage):
    """
    Calculates rms voltage from peak voltage for AC sine waves.

    Input:
    *   peak_voltage: Vp (Volts)

    Output:
    *   rms_voltage: Vrms (Volts)
    """
    retval = 0

    try:
        retval = (1 / math.sqrt(2)) * peak_voltage
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_rms_from_peak_to_peak(peak_to_peak_voltage):
    """
    Calculates rms voltage from peak to peak voltage for AC sine waves.

    Input:
    *   peak_to_peak_voltage: Vp-p (Volts)

    Output:
    *   rms_voltage: Vrms (Volts)
    """
    retval = 0

    try:
        retval = (1 / (2 * math.sqrt(2))) * peak_to_peak_voltage
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_rms_from_average(average_voltage):
    """
    Calculates rms voltage from average voltage for AC sine waves.

    Input:
    *   average_voltage: Vav (Volts)

    Output:
    *   rms_voltage: Vrms (Volts)
    """
    retval = 0

    try:
        retval = (PI / (2 * math.sqrt(2))) * average_voltage
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_average_from_peak(peak_voltage):
    """
    Calculates average voltage from peak voltage for AC sine waves.

    Input:
    *   peak_voltage: Vp (Volts)

    Output:
    *   average_voltage: Vav (Volts)
    """
    retval = 0

    try:
        retval = (2 * peak_voltage) / PI
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_average_from_peak_to_peak(peak_to_peak_voltage):
    """
    Calculates average voltage from peak to peak voltage for AC sine waves.

    Input:
    *   peak_to_peak_voltage: Vp-p (Volts)

    Output:
    *   average_voltage: Vav (Volts)
    """
    retval = 0

    try:
        retval = peak_to_peak_voltage / PI
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_average_from_rms(rms_voltage):
    """
    Calculates average voltage from rms voltage for AC sine waves.

    Input:
    *   rms_voltage: Vrms (Volts)

    Output:
    *   average_voltage: Vav (Volts)
    """
    retval = 0

    try:
        retval = rms_voltage * ((2 * math.sqrt(2)) / PI)
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_from_peak_to_peak(peak_to_peak_voltage):
    """
    Calculates peak voltage from peak to peak voltage for AC sine waves.

    Input:
    *   peak_to_peak_voltage: Vp-p (Volts)

    Output:
    *   peak_voltage: Vp (Volts)
    """
    retval = 0

    try:
        retval = peak_to_peak_voltage * 0.5
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_from_rms(rms_voltage):
    """
    Calculates peak voltage from rms voltage for AC sine waves.

    Input:
    *   rms_voltage: Vrms (Volts)

    Output:
    *   peak_voltage: Vp (Volts)
    """
    retval = 0

    try:
        retval = rms_voltage * math.sqrt(2)
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_from_average(average_voltage):
    """
    Calculates peak voltage from average voltage for AC sine waves.

    Input:
    *   average_voltage: Vav (Volts)

    Output:
    *   peak_voltage: Vp (Volts)
    """
    retval = 0

    try:
        retval = average_voltage * (PI / 2)
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_to_peak_from_average(average_voltage):
    """
    Calculates peak to peak voltage from average voltage for AC sine waves.

    Input:
    *   average_voltage: Vav (Volts)

    Output:
    *   peak_to_peak_voltage: Vp-p (Volts)
    """
    retval = 0

    try:
        retval = average_voltage * PI
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_to_peak_from_rms(rms_voltage):
    """
    Calculates peak to peak voltage from rms voltage for AC sine waves.

    Input:
    *   rms_voltage: Vrms (Volts)

    Output:
    *   peak_to_peak_voltage: Vp-p (Volts)
    """
    retval = 0

    try:
        retval = rms_voltage * (2 * math.sqrt(2))
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_peak_to_peak_from_peak(peak_voltage):
    """
    Calculates peak to peak voltage from peak voltage for AC sine waves.

    Input:
    *   peak_voltage: Vp (Volts)

    Output:
    *   peak_to_peak_voltage: Vp-p (Volts)
    """
    retval = 0

    try:
        if abs(peak_voltage) >= 0:  # Forces TypeError for non-numerics
            retval = peak_voltage * 2
        else:
            raise TypeError
    except TypeError:
        raise TypeError("The parameter you entered was not valid")

    return retval


def voltage_divider_c(voltage_in, impedance, capacitive_reactance):
    """
    Calculates output voltage when a capacitor is used as a voltage divider.

    Inputs:
    *   voltage_in: Vin (Volts)
    *   impedance: Z (Ohms)
    *   capacitive_reactance: Xc (Ohms)

    Output:
    *   voltage_out: Vout (Volts)
    """
    retval = 0

    try:
        retval = voltage_in * (capacitive_reactance / impedance)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Impedance cannot be 0")

    return retval


# ========= #
# IMPEDANCE #
# ========= #
def impedance_rc(resistance, capacitive_reactance):
    """
    Calculate impedance in an RC (resistor capacitor) circuit.

    Inputs:
    *   resistance: R (Ohms)
    *   capacitive_reactance: Xc (Ohms).

    Output:
    *   impedance: Z (Ohms)
    """
    retval = 0

    try:
        retval = math.sqrt(pow(resistance, 2) + pow(capacitive_reactance, 2))
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def impedance_rcl(resistance, capacitive_reactance, inductive_reactance):
    """
    Calculate impedance in an RCL (resistor capacitor inductor) circuit.

    Inputs:
    *   resistance: R (Ohms)
    *   capacitive_reactance: Xc (Ohms)
    *   inductive_reactance: Xl (Ohms)

    Output:
    *   impedance: Z (Ohms)
    """
    retval = 0

    try:
        retval = math.sqrt(pow(resistance, 2) + pow(inductive_reactance - capacitive_reactance, 2))
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def impedance_rcl_phase_angle(resistance, capacitive_reactance, inductive_reactance):
    """
    Calculates the phase angle (Degrees) for impedance vectors in an RCL (resistor capacitor inductor) circuit.

    Inputs:
    *   resistance: R (Ohms)
    *   capacitive_reactance: Xc (Ohms)
    *   inductive_reactance: Xl (Ohms)

    Output:
    *   phase_angle: 𝜃 (Degrees)
    """
    retval = 0

    try:
        retval = math.degrees(math.atan((inductive_reactance - capacitive_reactance) / resistance))
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Resistance cannot be 0")

    return retval


# ======================== #
# AMPLIFIERS / ATTENUATORS #
# ======================== #
def gain(input_value, output_value):
    """
    Calculates the gain ratio of either voltage, current or power.  If greater than 1 it is an amplification,
    and if less than 1 it is an attenuation.

    Inputs:
    *   input_value: voltage: V (Volts), current: I (Amperes) or power: P (Watts)
    *   output_value: voltage: V (Volts), current: I (Amperes) or power: P (Watts)

    Output:
    *   gain: A (ratio)
    """
    retval = 0

    try:
        retval = output_value / input_value
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Input Value cannot be 0")

    return retval


def gain_db(input_value, output_value):
    """
    Calculates the dB gain of either voltage or current. If positive it is an amplification, and if negative it
    is an attenuation.

    Inputs:
    *   input_value: voltage: V (Volts) or current: I (Amperes)
    *   output_value: voltage: V (Volts) or current: I (Amperes)

    Output:
    *   gain: A (deciBels)
    """
    retval = 0

    try:
        gain_ratio = gain(input_value, output_value)
        retval = 20 * math.log10(gain_ratio)
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Input Value cannot be 0")

    return retval


def gain_db_power(input_power, output_power):
    """
    Calculates the dB gain of power. If positive it is an amplification, and if negative it is an attenuation.

    Inputs:
        input_value: power: P (Watts)
        output_value: power: P (Watts)

    Output:
        power gain: A (deciBels)
    """
    retval = 0

    try:
        db = gain_db(input_power, output_power)
        retval = db / 2
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("Input Value cannot be 0")

    return retval


# ====== #
# COMMON #
# ====== #
def _sums(items: tuple):
    """
    Sums values in a tuple of numeric values.

    Inputs:
    *   items: any

    Output:
    *   sum: any
    """
    retval = 0

    try:
        if len(items) == 0:
            raise ValueError

        for item in items:
            retval += item
    except ValueError:
        raise ValueError("At least one parameter must be entered")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")

    return retval


def _inverse_sums(items: tuple):
    """Inverts the sum of values in a tuple of numeric values.

    Inputs:
    *   items: any

    Output:
    *   inverse_sum: any
    """
    retval = 0
    total = 0

    try:
        if len(items) == 0:
            raise ValueError

        for item in items:
            total += (1 / item)

        retval = 1 / total
    except ValueError:
        raise ValueError("At least one parameter must be entered")
    except TypeError:
        raise TypeError("Function expected a tuple of numeric values")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval


def _tau(item_a, item_b):
    """Returns 2 * PI times the inputs.

    Inputs:
    *   items a: any
    *   items b: any

    Output:
    *   tau'd inputs: any
    """
    retval = 0

    try:
        retval = 2 * PI * item_a * item_b
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")

    return retval


def _inverse_tau(item_a, item_b):
    """Returns the inverse of 2 * PI times the inputs.

    Inputs:
    *   items a: any
    *   items b: any

    Output:
    *   inverse tau'd inputs: any
    """
    retval = 0

    try:
        tau = _tau(item_a, item_b)
        retval = 1 / tau
    except TypeError:
        raise TypeError("One or more of the parameters you entered was not valid")
    except ZeroDivisionError:
        raise ZeroDivisionError("None of the parameters can be 0")

    return retval
