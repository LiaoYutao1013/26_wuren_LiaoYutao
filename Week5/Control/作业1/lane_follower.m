%% 第二问：轨迹跟踪
    clear; clc; close all

    % 车辆参数
    lfr = 2.168 + 1.907; % 轴距 L
    dt = 0.01;
    v = 15; 
    sim_steps = 2000;
    
    % 参考轨迹 (正弦曲线)
    X_ref = 0:0.1:200; 
    Y_ref = 10 * sin(X_ref / 15); 

    % 初始车辆状态 
    X = X_ref(1); Y = Y_ref(1) + 3; phi = 0; 
    X_vec = zeros(1, sim_steps); Y_vec = zeros(1, sim_steps);

    % PID控制器误差初始化
    integral_error = 0;
    previous_error = 0;
    e_vec = zeros(1, sim_steps); % 记录误差变化

    for ii = 1:sim_steps
        X_vec(ii) = X; Y_vec(ii) = Y;
    
    
        % ===============================================================
    
        % ================= TODO 2.1: 实现某种跟踪算法 =================
    
        % 选PID算法进行小车控制。
        % 思路：1.计算当前车辆位置与参考轨迹的误差（距离，横向误差）；2.根据误差调整前轮转角 sigma。
        % 
        % 计算当前车辆位置与参考轨迹的最近点
        distances = sqrt((X_ref - X).^2 + (Y_ref - Y).^2);
        [~, closest_idx] = min(distances);
        e = distances(closest_idx); % 误差
        % PID控制器参数
        Kp = 0.5; Ki = 0.1; Kd = 0.05;
        % 更新积分误差和微分误差
        integral_error = integral_error + e * dt;
        derivative_error = (e - previous_error) / dt;
        previous_error = e;
        e_vec(ii) = e; % 记录误差变化
        % 计算转向角 sigma 
        sigma = Kp * e + Ki * integral_error + Kd * derivative_error;

        % ===============================================================

        % ================= TODO 2.2: 车辆状态更新 =================
        % 提示: 将刚才求得的转向角 sigma 代入运动学模型（复用第一问代码），更新 X, Y, phi。
    
        phi_dot = v / lfr * tan(sigma);
        phi = phi + phi_dot * dt;
        X = X + v * cos(phi) * dt;
        Y = Y + v * sin(phi) * dt;

        % ===============================================================
    
        % 到达终点提前结束
        if X >= X_ref(end)
            break; 
        end
    end
        % 绘图对比
    figure; hold on; grid on;
    plot(X_ref, Y_ref, 'k--', 'LineWidth', 2);
    plot(X_vec(1:ii), Y_vec(1:ii), 'r-', 'LineWidth', 2);
    legend('参考规划轨迹', '实际行驶轨迹');
    title(['PID跟踪 (步数: ', num2str(ii), ')']);
    xlabel('X [m]'); ylabel('Y [m]'); axis equal;

