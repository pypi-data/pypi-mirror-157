from py_ballisticcalc.projectile import *
from py_ballisticcalc.drag import *
from py_ballisticcalc.weapon import *
from py_ballisticcalc.trajectory_calculator import *
from py_ballisticcalc.atmosphere import *
from py_ballisticcalc.shot_parameters import *
from py_ballisticcalc.bmath import unit

bc = BallisticCoefficient(0.223, DragTableG7)
projectile = ProjectileWithDimensions(bc, unit.Distance(0.308, unit.DistanceInch).validate(),
                                      unit.Distance(1.282, unit.DistanceInch).validate(),
                                      unit.Weight(168, unit.WeightGrain).validate())
ammo = Ammunition(projectile, unit.Velocity(2750, unit.VelocityFPS).validate())
zero = ZeroInfo(unit.Distance(100, unit.DistanceMeter).validate())
twist = TwistInfo(TwistRight, unit.Distance(11.24, unit.DistanceInch).validate())
weapon = Weapon.create_with_twist(unit.Distance(2, unit.DistanceInch).validate(), zero, twist)
atmosphere = Atmosphere()
shot_info = ShotParameters(unit.Angular(4.221, unit.AngularMOA).validate(),
                           unit.Distance(1001, unit.DistanceMeter).validate(),
                           unit.Distance(100, unit.DistanceMeter).validate())
wind = WindInfo.create_only_wind_info(unit.Velocity(5, unit.VelocityMPH).validate(),
                                      unit.Angular(-45, unit.AngularDegree).validate())

calc = TrajectoryCalculator()
data = calc.trajectory(ammo, weapon, atmosphere, shot_info, wind)

for d in data:
    distance = d.travelled_distance
    meters = distance.convert(unit.DistanceMeter)
    velocity = d.velocity.convert(unit.VelocityMPS)
    mach = round(d.mach_velocity, 4)
    energy = d.energy
    time = round(d.time.total_seconds, 4)
    ogv = d.optimal_game_weight.get_in(unit.WeightPound)
    path = d.drop.convert(unit.DistanceCentimeter)
    hold = d.drop_adjustment.get_in(unit.AngularMOA) if distance.v > 1 else None
    windage = d.windage.convert(unit.DistanceCentimeter)
    wind_adjustment = d.windage_adjustment.get_in(unit.AngularMOA) if distance.v > 1 else None
    print(
        f'Distance: {meters}, Velocity: {velocity}, '
        f'Mach: {mach}, Energy: {energy}, '
        f'Time: {time}s, Path: {path}, Windage: {windage}'
    )
