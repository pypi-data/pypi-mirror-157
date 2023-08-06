## This is the Mobility Virtual Environment, or MoVE.

MoVE is open-source software released under the GNU Public License, version 3 (GPLv3).  

MoVE is maintained at these these locations:   
  * Source code on GitLab: https://gitlab.com/comperem/move  
  * Description on GitLab.io: https://comperem.gitlab.io/move  
  * Google Groups for discussion: https://groups.google.com/forum/#!forum/mobility_virtual_environment
  

***
### Overview
MoVE is designed to simulate and test multi-vehicle scenarios with a combination of
real and virtual autonomous vehicles in a common coordinate frame with a common timestamp.
Simulated vehicles are launched as separate computer processes, each with their own
behavior, numerical integration, and communication threads. A soft-real-time subsystem
integrates a set of mobility ODEs at the same rate as wall-clock time.
Equations of motion are written in body-fixed `xyz` coordinates and transformed into
the inertial frame, `XYZ`. The solution in `XYZ` represents vehicle motion in a
3D orthogonal coordinate frame.
Coordinate transformations to and from the `XYZ` frame and latitude and longitude
coordinates using the WGS-84 geodetic model is built in with the
[UTM](https://pypi.org/project/utm/) python library.

Vehicle-to-vehicle (V2V) communications allows each vehicle to know the status
of others nearby. This can influence behaviors or be used as triggers in a
mission scheduler to orchestrate complex multi-vehicle scenarios.

Motion from real vehicles or pedestrians can be incorporated in the same virtual
environment with simulated vehicles using a vehicle process with no dynamic
equations of motion. This model type is called a live-GPS-follower.
When a real person or real vehicle moves and sends GPS latitude and longitude
coordinates to the live-GPS-follower, the motion in the virtual world is based on
the real motion of the real person or vehicle in the real world.

A lat/lon origin for virtual placement near the same lat/lon location as the real
vehicles or pedestrians allows real and virtual vehicles to interact in the virtual
environment in real time.

The MoVE environment allows autonomy algorithms such as sense-and-avoid and
search-and-rescue (SAR) algorithm development to progress from simulation-only
to mixed simulation-and-real testing to all real vehicles testing in the real world.

The MoVE environment is also ideally suited for FAA regulators and researchers
to develop and test Unmanned Aircraft System Traffic Management (UTM) regulations
and collision avoidance to improve public safety. The detect-and-avoid (DAA)
problem is complex and MoVE can help define scenarios for detect-and-avoid.

A configuration file allows researchers to share scenario and vehicle settings
to help collaboration on multi-vehicle scenarios.

***
### Software Language:

MoVE is written nearly entirely in
[Python 3](https://www.python.org/) with m-file post-processing scripts that work in [Matlab](www.mathworks.com)
(and probably [Octave](https://www.gnu.org/software/octave/)).

A list of MoVE's characteristics:
- MoVE is primarily a protoyping and testing environment for multi-vehicle coordination
and behavior development. MoVE is decidedly non-graphical and is mainly a collection
of command line programs to launch and manage N vehicle model processes.
- A 2D top-down, or plan view with Google maps background using the open-source
[Bokeh](bokeh.pydata.org) library is provided for 2D visualization during runtime or playback.
- Each vehicle process may represent a ground, air, surface, or underwater vehicle with some
mobility in an orthogonal 3D space. 
- Multiple vehicle processes communicate with MoVE Core by providing position and health status
updates periodically
- MoVE Core aggregates all vehicle positons and constructs the scenario `State`
and logs the time history of `State` as a csv file.
- Individual vehicle processes also log vehicle state and bi-directional communications
with MoVE core for debugging and developing behaviors and communications.

MoVE is a work in progress and a website with installation and runtime
instructions are forthcoming.

***
### GNU Public License, version 3:
  - The MoVE software is open-source and freely available under the terms of the GNU Public License, version 3 (GPLv3).
  - The GPLv3 is endorsed by the Open Source Initiative and is described here: https://opensource.org/licenses/gpl-3.0.html
  - The GPLv3 is a copyleft license which means you may redistribute it only under the same GPLv3 license terms.
    The intent behind the copyleft is to build a strong user community and ensure the original open-source software is
    not made proprietary or no longer open-source.
    Read more here about copyleft here: https://opensource.com/resources/what-is-copyleft




***
  Marc Compere, Ph.D.  
  comperem@erau.edu  
  created : 14 July 2018  
  modified: 21 Jun 2022
