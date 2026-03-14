"""
CLI entry point for Hong Kong Universities Master's Admissions Collector.

Usage:
    python -m hk_admissions.main --output-dir ./output --formats all
    python -m hk_admissions.main --university hku --formats excel,markdown
    python -m hk_admissions.main --list-universities
"""

import argparse
import logging
import sys
from datetime import datetime

from hk_admissions.collector import HKAdmissionsCollector
from hk_admissions.exporters import export_all, EXPORTER_MAP
from hk_admissions.models import HK_UNIVERSITIES


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect Hong Kong universities master's programme admissions information.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect all universities, export to all formats
  python -m hk_admissions.main --output-dir ./output --formats all

  # Collect specific university, export to Excel and Markdown
  python -m hk_admissions.main --university hku --formats excel,markdown

  # Collect multiple universities
  python -m hk_admissions.main --university hku,cuhk,hkust --formats all

  # List supported universities
  python -m hk_admissions.main --list-universities

  # Verbose output for debugging
  python -m hk_admissions.main --verbose --output-dir ./output
        """,
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="./output",
        help="Output directory for generated files (default: ./output)",
    )
    parser.add_argument(
        "--formats", "-f",
        default="all",
        help=(
            "Comma-separated list of export formats. "
            f"Available: {', '.join(EXPORTER_MAP.keys())}, all (default: all)"
        ),
    )
    parser.add_argument(
        "--university", "-u",
        default=None,
        help=(
            "Comma-separated list of university keys to collect. "
            "Default: all universities. "
            f"Available: {', '.join(HK_UNIVERSITIES.keys())}"
        ),
    )
    parser.add_argument(
        "--filename-prefix",
        default="hk_master_admissions",
        help="Filename prefix for output files (default: hk_master_admissions)",
    )
    parser.add_argument(
        "--list-universities",
        action="store_true",
        help="List all supported universities and exit.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Maximum concurrent scraper threads (default: 3)",
    )
    return parser.parse_args()


def list_universities():
    """Print supported universities."""
    print("\n🎓 Supported Hong Kong Universities:\n")
    print(f"{'Key':<12} {'Abbreviation':<10} {'Name':<50} {'Chinese Name'}")
    print("-" * 100)
    for key, config in sorted(HK_UNIVERSITIES.items()):
        print(f"{key:<12} {config.abbreviation:<10} {config.name:<50} {config.name_cn}")
    print(f"\nTotal: {len(HK_UNIVERSITIES)} universities")
    print(f"\nAdmissions URLs:")
    for key, config in sorted(HK_UNIVERSITIES.items()):
        print(f"  {config.abbreviation:<8} {config.programs_list_url}")


def main():
    """Main entry point."""
    args = parse_args()
    setup_logging(args.verbose)

    # List universities mode
    if args.list_universities:
        list_universities()
        return

    logger = logging.getLogger(__name__)
    print("\n" + "=" * 70)
    print("🎓 Hong Kong Universities Master's Admissions Collector")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Initialize collector
    collector = HKAdmissionsCollector(max_workers=args.max_workers)

    # Collect data
    if args.university:
        uni_keys = [k.strip().lower() for k in args.university.split(",")]
        print(f"📡 Collecting data from: {', '.join(uni_keys)}")
        print()

        if len(uni_keys) == 1:
            try:
                programs = collector.collect_university(uni_keys[0])
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
        else:
            try:
                programs = collector.collect_multiple(uni_keys)
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
    else:
        print("📡 Collecting data from ALL Hong Kong universities...")
        print()
        programs = collector.collect_all()

    # Summary
    summary = collector.get_summary()
    print(f"\n📊 Collection Summary:")
    print(f"   Total programmes: {summary['total_programs']}")
    if summary.get("universities"):
        for uni, count in sorted(summary["universities"].items()):
            print(f"   - {uni}: {count} programmes")
    print()

    if not programs:
        print("⚠️  No programmes collected. Please check your network connection and try again.")
        sys.exit(1)

    # Determine formats
    if args.formats.lower() == "all":
        formats = list(EXPORTER_MAP.keys())
    else:
        formats = [f.strip().lower() for f in args.formats.split(",")]

    print(f"📝 Exporting to formats: {', '.join(formats)}")
    print(f"📁 Output directory: {args.output_dir}")
    print()

    # Export
    results = export_all(
        programs=programs,
        output_dir=args.output_dir,
        filename_prefix=args.filename_prefix,
        formats=formats,
    )

    # Final summary
    print(f"\n{'=' * 70}")
    print("✅ Export Complete!")
    print(f"{'=' * 70}")
    for fmt, filepath in results.items():
        if filepath:
            print(f"   📄 {fmt.upper():<10} → {filepath}")
        else:
            print(f"   ❌ {fmt.upper():<10} → Failed")
    print()
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


if __name__ == "__main__":
    main()
