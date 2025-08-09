def rk4( f, y, dt):
    k1 = f(y)
    k2 = f(y + k1 * dt * 0.5)
    k3 = f(y + k2 * dt * 0.5)
    k4 = f(y + k3 * dt)
    
    y_dt = y + dt * (k1 + 2*k2 + 2*k3 + k4)/6
    return y_dt