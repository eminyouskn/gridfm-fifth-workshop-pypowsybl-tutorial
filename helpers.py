"""
Helper functions for the Hands-On Power System Analysis with PyPowSyBl tutorial.
GridFM Workshop — Harvard, March 2026.
"""

import statistics as stats
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import pypowsybl as pp
import pypowsybl.loadflow as lf
import pypowsybl.network as pn
import pypowsybl.report as rp
from pypowsybl._pypowsybl import BalanceType
from pypowsybl_jupyter import network_explorer

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)

import_parameters = {
    "iidm.import.cgmes.create-active-power-control-extension": "true",
    "iidm.import.cgmes.post-processors": "cgmesGLImport"
}

sld_parameters = pn.SldParameters(
    use_name=True, center_name=True, diagonal_label=True,
    nodes_infos=True, tooltip_enabled=True, topological_coloring=True,
    component_library='FlatDesign', active_power_unit='MW',
    reactive_power_unit='MVAr'
)


def get_six_buses() -> pn.Network:
    """Creates the 6-bus Metrix tutorial network with active power control extensions."""
    net = pn.create_metrix_tutorial_six_buses_network()
    for idx, _ in net.get_generators().iterrows():
        net.create_extensions(
            'activePowerControl', id=idx, droop=1.3,
            participate=True, participation_factor=1.0
        )
    return net


def get_microgrid_t4() -> pn.Network:
    """Loads the ENTSO-E CGMES v2.4.15 MicroGrid Test Configuration T4."""
    return pn.load(
        'data/microgrid_t4.zip',
        import_parameters,
        post_processors=['replaceTieLinesByLines']
    )


def get_relicapgrid_belgovia() -> pn.Network:
    """Loads the ReliCapGrid Belgovia IGM."""
    return pn.load(
        file="data/relicapgrid/igm_belgovia",
        parameters={
            "iidm.import.cgmes.boundary-location": "data/relicapgrid/bds",
        }
    )


def get_realgrid() -> pn.Network:
    """Loads the ENTSO-E CGMES Real Grid Test Configuration with geographical data."""
    return pn.load(
        "data/RealGridTestConfiguration.zip",
        {"iidm.import.cgmes.post-processors": "cgmesGLImport"}
    )


def get_rte_6515() -> pn.Network:
    """Loads the RTE 6515-bus network and fixes phase tap changer steps."""
    net = pp.network.load("data/case6515rte.mat")
    ptc = net.get_phase_tap_changers(attributes=["tap"])
    steps = net.get_phase_tap_changer_steps(attributes=["alpha"])
    taps = ptc["tap"].dropna().astype(int)
    idx = [(tid, int(tap)) for tid, tap in taps.items() if (tid, int(tap)) in steps.index]
    df_upd = steps.loc[idx, ["alpha"]].copy()
    df_upd["alpha"] = 0.0
    net.update_phase_tap_changer_steps(df_upd)
    return net


def run_lf(network, use_reactive_limits=True, detailed_report=False, use_defaults=True, **kwargs):
    """Runs an AC load flow and prints summary."""
    if use_defaults:
        reported_features = 'NEWTON_RAPHSON_LOAD_FLOW' if detailed_report else ''
        lf_parameters = lf.Parameters(
            distributed_slack=True,
            read_slack_bus=False,
            use_reactive_limits=use_reactive_limits,
            balance_type=BalanceType.PROPORTIONAL_TO_GENERATION_PARTICIPATION_FACTOR,
            provider_parameters={
                'referenceBusSelectionMode': 'GENERATOR_REFERENCE_PRIORITY',
                'reportedFeatures': reported_features,
                'svcVoltageMonitoring': 'false'
            },
            **kwargs
        )
    else:
        lf_parameters = lf.Parameters(
            use_reactive_limits=use_reactive_limits,
            **kwargs
        )
    report = rp.ReportNode('demo', 'demo')
    t0 = time.time()
    lf_result = lf.run_ac(network=network, parameters=lf_parameters, report_node=report)
    result = lf_result[0]
    print(f'Power Flow Execution Time: {(time.time() - t0):.3f} s')
    print(f'Status: {result.status_text}, Iterations: {result.iteration_count}, '
          f'Distributed P: {result.distributed_active_power:.2f} MW')
    return lf_result, report


def plot_curve(network, injection_id):
    """Plots reactive capability curve for a given injection."""
    injection = network.get_injections().loc[injection_id]
    name = ''
    if injection['type'] == 'HVDC_CONVERTER_STATION':
        name = network.get_vsc_converter_stations().loc[injection_id]['name']
    elif injection['type'] == 'GENERATOR':
        name = network.get_generators().loc[injection_id]['name']
    curve = network.get_reactive_capability_curve_points().loc[injection_id].reset_index(drop=True)
    py1 = curve.p.tolist()
    py2 = list(reversed(curve.p.tolist()))
    qminx = curve.min_q.tolist()
    qmaxx = list(reversed(curve.max_q.tolist()))
    plt.figure(figsize=(4, 4))
    plt.axis('equal')
    plt.axhline(y=0, color='k', lw=0.5)
    plt.axvline(x=0, color='k', lw=0.5)
    x = qminx + qmaxx + [qminx[0]]
    y = py1 + py2 + [py1[0]]
    plt.fill(x, y, 'lightskyblue')
    plt.plot(x, y, 'k', lw=2)
    plt.axvline(-injection.q, color='g', lw=2)
    plt.text(5, -injection.p + 5, f'{-injection.p:.1f} MW', color='tomato')
    plt.text(-injection.q + 5, -injection.p + 10, f'{-injection.q:.1f} Mvar',
             rotation='vertical', color='tomato')
    plt.axhline(-injection.p, color='g', lw=2)
    plt.grid(True, which='both')
    plt.xlabel('Q (Mvar)')
    plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f Mvar'))
    plt.xticks(rotation=90)
    plt.ylabel('P (MW)')
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f MW'))
    plt.title(f'{name} Reactive Capability Curve')
    plt.show()
