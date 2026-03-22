#!/usr/bin/env python3
"""
Deployment Calculator — CLI tool for site assessment.

Estimates wave energy potential, iron delivery feasibility, and
pH restoration capacity for a coastal restoration deployment.

Usage:
    python community-tools/deployment_calculator.py \\
        --wave-height 1.0 --wave-period 8.0 \\
        --temperature 15.0 --salinity 35.0 --pH 8.05

    python community-tools/deployment_calculator.py --preset la-jolla
    python community-tools/deployment_calculator.py --preset river-mouth
    python community-tools/deployment_calculator.py --preset tropical-reef
"""

import argparse
import sys
import os

# Add equations directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..', 'equations'))

from ocean_restoration_simulation import (
    SiteConfig, run_integrated_assessment, format_assessment,
    LA_JOLLA, RIVER_MOUTH, TROPICAL_REEF,
)


PRESETS = {
    "la-jolla": LA_JOLLA,
    "river-mouth": RIVER_MOUTH,
    "tropical-reef": TROPICAL_REEF,
}


def main():
    parser = argparse.ArgumentParser(
        description="Ocean Restoration Deployment Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --preset la-jolla
  %(prog)s --wave-height 1.2 --wave-period 10 --pH 8.0
  %(prog)s --wave-height 0.8 --owc-width 3 --turbine check_valve
        """,
    )

    parser.add_argument("--preset", choices=list(PRESETS.keys()),
                        help="Use a predefined site configuration")
    parser.add_argument("--name", default="Custom Site",
                        help="Site name for report header")

    # Wave conditions
    wave = parser.add_argument_group("Wave conditions")
    wave.add_argument("--wave-height", type=float, default=1.0,
                      help="Significant wave height in meters (default: 1.0)")
    wave.add_argument("--wave-period", type=float, default=8.0,
                      help="Peak wave period in seconds (default: 8.0)")

    # Seawater
    water = parser.add_argument_group("Seawater conditions")
    water.add_argument("--temperature", type=float, default=15.0,
                       help="Water temperature in °C (default: 15.0)")
    water.add_argument("--salinity", type=float, default=35.0,
                       help="Salinity in PSU (default: 35.0)")
    water.add_argument("--salinity-low", type=float, default=None,
                       help="Low salinity for gradient (PSU, e.g., river water)")
    water.add_argument("--pH", type=float, default=8.05, dest="ph",
                       help="Current seawater pH (default: 8.05)")
    water.add_argument("--current-speed", type=float, default=0.3,
                       help="Ocean current speed in m/s (default: 0.3)")

    # Device
    dev = parser.add_argument_group("Device parameters")
    dev.add_argument("--owc-width", type=float, default=5.0,
                     help="OWC chamber width in meters (default: 5.0)")
    dev.add_argument("--owc-depth", type=float, default=3.0,
                     help="OWC chamber depth in meters (default: 3.0)")
    dev.add_argument("--turbine", default="wells",
                     choices=["wells", "impulse", "check_valve"],
                     help="Turbine type (default: wells)")

    # Iron
    iron = parser.add_argument_group("Iron release")
    iron.add_argument("--iron-release", type=float, default=500.0,
                      help="Iron release rate in μg/hr (default: 500)")
    iron.add_argument("--no-iron", action="store_true",
                      help="Disable iron release modeling")

    # pH target
    ph_grp = parser.add_argument_group("pH restoration")
    ph_grp.add_argument("--target-pH", type=float, default=8.15,
                        dest="target_ph",
                        help="Target pH for restoration (default: 8.15)")
    ph_grp.add_argument("--flow-rate", type=float, default=50.0,
                        help="Electrochemical cell flow rate in L/min (default: 50)")

    args = parser.parse_args()

    if args.preset:
        config = PRESETS[args.preset]
    else:
        config = SiteConfig(
            name=args.name,
            wave_height_m=args.wave_height,
            wave_period_s=args.wave_period,
            temperature_C=args.temperature,
            salinity_psu=args.salinity,
            salinity_low_psu=args.salinity_low if args.salinity_low else args.salinity,
            pH=args.ph,
            current_speed_m_s=args.current_speed,
            owc_width_m=args.owc_width,
            owc_depth_m=args.owc_depth,
            turbine_type=args.turbine,
            iron_release_ug_hr=0.0 if args.no_iron else args.iron_release,
            target_pH=args.target_ph,
            flow_rate_L_min=args.flow_rate,
        )

    result = run_integrated_assessment(config)
    print(format_assessment(result, config))


if __name__ == "__main__":
    main()
