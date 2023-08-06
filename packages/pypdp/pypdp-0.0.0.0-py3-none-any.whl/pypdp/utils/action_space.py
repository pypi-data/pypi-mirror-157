def default_action_space(env, allow_zero_tour: bool = False):
    visitable_pickup_idx = list(env.manager.active_pickup_idx)
    visitable_delivery_idx = list(env.manager.target_vehicle.visitable_delivery_idx)
    action_space = visitable_pickup_idx + visitable_delivery_idx

    finish_delivery = len(visitable_delivery_idx) == 0
    not_last_agent = env.m - (len(env.manager.to_depot_vehicle_idx) + len(env.manager.completed_vehicle_idx)) > 1

    if allow_zero_tour:
        cond = finish_delivery and not_last_agent
    else:
        c = len(env.manager.target_vehicle.tour) > 1
        cond = finish_delivery and not_last_agent and c

    if cond:
        action_space += [0]

    finished = len(env.manager.completed_delivery_idx) == env.n
    if finished:
        action_space = [0]

    return action_space
