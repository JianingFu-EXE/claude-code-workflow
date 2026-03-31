# Problem Statement

## The Challenge of Model-Based Control Under Fault Conditions

In engineering practice, the actuator fault phenomenon is pervasive due mainly to the physical degradation of pitch actuators operating in harsh marine environments. Over the operational lifetime of a floating offshore wind turbine, pitch bearing wear, hydraulic system leakage, and blade surface erosion progressively degrade control authority. If these fault conditions are not taken into account in the controller design procedure, it is possible that the control performance degrades or even the overall stability is compromised.

## Widely Studied But Insufficient

A wealth of literature has implemented fault-tolerant control approaches for wind turbine pitch systems. Traditional methods include gain-scheduled PI controllers with fault detection and isolation modules, linear parameter-varying controllers, and sliding mode controllers designed for specific fault scenarios. In particular, robust H-infinity controllers have been investigated for their ability to handle bounded uncertainties in the plant model.

However, these conventional fault-tolerant strategies share a fundamental limitation: they rely on accurate mathematical models of both the nominal system and the fault dynamics. For floating offshore wind turbines, obtaining such models is exceptionally challenging due to the coupled aero-hydro-servo-elastic dynamics that defy simple linearization. The generalisability of much published research on this issue is problematic, as most studies have only been carried out using simplified onshore turbine models that neglect platform motion.
