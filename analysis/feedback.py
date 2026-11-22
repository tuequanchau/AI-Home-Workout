# File: analysis/feedback.py

# --- CÁC NGƯỠNG ĐÁNH GIÁ KỸ THUẬT ---
SQUAT_DEEP_WARNING_ANGLE = 65.0     # Ngồi quá sâu dễ gây áp lực khớp gối
SQUAT_DESCEND_MID_ANGLE = 120.0     # Ngưỡng giữa quá trình hạ người
SQUAT_STANDING_MIN_ANGLE = 160.0    # Góc tối thiểu để tính là đứng thẳng hoàn toàn
SQUAT_MAX_ASYMMETRY = 15.0          # Độ lệch tối đa cho phép giữa gối trái và phải (độ)
SQUAT_MAX_TORSO_LEAN = 45.0         # Độ nghiêng lưng tối đa về phía trước (độ)

JJ_CLOSED_LEG_MAX = 1.15            # Tỷ lệ khoảng cách chân tối đa khi khép
JJ_OVERWIDE_LEG_MAX = 2.4           # Tỷ lệ khoảng cách chân quá rộng dễ mất thăng bằng


def get_squat_feedback(
    angle,
    state,
    left_angle=None,
    right_angle=None,
    torso_lean=None,
    knee_valgus=False,
    rep_count=0,
):
    """
    Phản hồi chi tiết cho bài tập Squat dựa trên góc gối, trạng thái và các lỗi tư thế.

    Parameters
    ----------
    angle : float | None
        Góc đầu gối trung bình (độ).
    state : str
        Trạng thái hiện tại: "STANDING", "DESCENDING", "BOTTOM", "ASCENDING".
    left_angle : float | None, optional
        Góc đầu gối trái để kiểm tra lệch trọng tâm.
    right_angle : float | None, optional
        Góc đầu gối phải để kiểm tra lệch trọng tâm.
    torso_lean : float | None, optional
        Góc nghiêng thân trên so với phương thẳng đứng (độ).
    knee_valgus : bool, optional
        True nếu hai đầu gối có xu hướng chụm vào trong.
    rep_count : int, optional
        Số lần tập đã hoàn thành.
    """
    if angle is None:
        return "Không nhận diện được góc đầu gối."

    # 1. Ưu tiên cảnh báo các lỗi kỹ thuật gây hại khớp khi đang chuyển động
    if state in ("DESCENDING", "BOTTOM", "ASCENDING"):
        if knee_valgus:
            return "Cảnh báo: Hai đầu gối đang chụm vào trong. Hãy đẩy nhẹ gối hướng theo mũi chân."

        if torso_lean is not None and torso_lean > SQUAT_MAX_TORSO_LEAN:
            return "Lưng đang cúi quá về phía trước. Hãy giữ ngực mở, mắt nhìn thẳng và siết cơ bụng."

        if left_angle is not None and right_angle is not None:
            diff = abs(left_angle - right_angle)
            if diff > SQUAT_MAX_ASYMMETRY:
                heavier_side = "trái" if left_angle < right_angle else "phải"
                return f"Lực đang dồn nhiều sang chân {heavier_side} (lệch {int(diff)}°). Hãy giữ trọng tâm cân bằng hai bên."

    # 2. Phản hồi chi tiết theo từng giai đoạn của bài Squat
    if state == "STANDING":
        if angle < SQUAT_STANDING_MIN_ANGLE:
            return "Hãy duỗi thẳng đầu gối hoàn toàn để kết thúc nhịp trước khi hạ người tiếp."
        if rep_count > 0 and rep_count % 5 == 0:
            return f"Tư thế đứng ổn định. Tuyệt vời, bạn đã hoàn thành {rep_count} rep! Tiếp tục nhé."
        return "Tư thế đứng ổn định. Tiếp tục thực hiện động tác."

    elif state == "DESCENDING":
        if angle > SQUAT_DESCEND_MID_ANGLE:
            return "Hãy tiếp tục hạ thấp cơ thể."
        return "Đang hạ người tốt. Cố gắng giữ lưng ổn định."

    elif state == "BOTTOM":
        if angle < SQUAT_DEEP_WARNING_ANGLE:
            return "Bạn đang hạ quá sâu (< 65°), dễ gây áp lực lên khớp gối. Hãy kiểm soát độ sâu và đẩy người lên."
        return "Đã đạt vị trí Squat. Bây giờ hãy đứng lên."

    elif state == "ASCENDING":
        return "Đang đứng lên. Hãy duỗi chân để hoàn thành động tác."

    return "Tiếp tục thực hiện Squat."


def get_jumping_jack_feedback(
    arms_up,
    leg_ratio,
    state,
    open_leg_ratio=1.5,
    arms_straight=True,
    rep_count=0,
):
    """
    Phản hồi chi tiết cho bài tập Jumping Jack.

    Parameters
    ----------
    arms_up : bool
        True nếu cổ tay đã đưa cao qua vai/đầu.
    leg_ratio : float | None
        Tỷ lệ khoảng cách hai mắt cá chân so với chiều rộng hông/vai.
    state : str
        Trạng thái hiện tại: "CLOSED" hoặc "OPEN".
    open_leg_ratio : float, optional
        Ngưỡng tỷ lệ chân mở đạt chuẩn.
    arms_straight : bool, optional
        True nếu hai cánh tay duỗi thẳng khi vung lên.
    rep_count : int, optional
        Số lần bật nhảy đã hoàn thành.
    """
    if leg_ratio is None:
        return "Không nhận diện được vị trí chân."

    if state == "CLOSED":
        if arms_up:
            return "Hãy khép chân và đưa hai tay xuống."

        if leg_ratio > JJ_CLOSED_LEG_MAX:
            return "Hãy khép hai chân lại."

        if rep_count > 0 and rep_count % 10 == 0:
            return f"Tư thế sẵn sàng. Bạn đã đạt {rep_count} lần bật nhảy, giữ vững nhịp độ nhé!"

        return "Tư thế sẵn sàng. Hãy bật nhảy mở tay và chân."

    elif state == "OPEN":
        if not arms_up:
            return "Hãy giơ hai tay cao hơn vai."

        if leg_ratio < open_leg_ratio:
            return "Hãy mở rộng hai chân hơn."

        if leg_ratio > JJ_OVERWIDE_LEG_MAX:
            return "Bạn đang mở chân quá rộng dễ mất thăng bằng. Hãy thu hẹp bước nhảy lại."

        if not arms_straight:
            return "Biên độ tốt, nhưng hãy giữ hai cánh tay thẳng hơn khi vung lên."

        return "Tư thế mở tốt. Hãy khép tay và chân lại."

    return "Tiếp tục thực hiện Jumping Jack."


def get_general_feedback(
    valid,
    missing_parts=None,
    distance_status=None,
    low_light=False,
):
    """
    Phản hồi về chất lượng khung hình và khả năng nhận diện cơ thể.

    Parameters
    ----------
    valid : bool
        True nếu các khớp trụ cột (vai, hông, gối) đều hiển thị rõ.
    missing_parts : list[str] | None, optional
        Danh sách vùng cơ thể đang bị khuất (ví dụ: ["chân", "mắt cá"]).
    distance_status : str | None, optional
        Trạng thái khoảng cách tới camera: "too_close", "too_far", hoặc "ok".
    low_light : bool, optional
        True nếu độ sáng khung hình quá thấp.
    """
    if not valid:
        if low_light:
            return "Ánh sáng môi trường hơi yếu khiến AI khó nhận diện khớp. Hãy bật thêm đèn."

        if distance_status == "too_close":
            return "Bạn đang đứng quá gần camera. Hãy lùi ra xa khoảng 1.5 - 2m để lấy trọn toàn thân."

        if distance_status == "too_far":
            return "Bạn đang đứng quá xa camera. Hãy tiến lại gần hơn một chút."

        if missing_parts:
            parts_text = ", ".join(missing_parts)
            return f"Camera chưa thấy rõ phần {parts_text}. Hãy điều chỉnh góc máy để thấy từ đầu đến chân."

        return "Vui lòng đứng ở vị trí camera có thể nhận diện rõ cơ thể."

    if distance_status == "too_close":
        return "Đã nhận diện cơ thể, nhưng bạn nên lùi nhẹ ra sau để không bị khuất bàn chân khi tập."

    return "Đang theo dõi chuyển động."


def get_rep_milestone_feedback(rep_count, exercise_name=""):
    """
    Tạo thông điệp khích lệ khi người tập đạt các cột mốc số lần lặp.
    """
    prefix = f"[{exercise_name}] " if exercise_name else ""

    if rep_count <= 0:
        return f"{prefix}Bắt đầu nào! Giữ nhịp thở đều và thực hiện đúng kỹ thuật."
    if rep_count == 1:
        return f"{prefix}Khởi đầu tốt! Đã hoàn thành rep đầu tiên."
    if rep_count % 10 == 0:
        return f"{prefix}Xuất sắc! Bạn đã chinh phục mốc {rep_count} rep. Giữ vững phong độ!"
    if rep_count % 5 == 0:
        return f"{prefix}Làm tốt lắm! Đã được {rep_count} rep rồi, cố lên!"

    return f"{prefix}Đã hoàn thành {rep_count} rep. Tiếp tục phát huy!"


def get_workout_summary_feedback(
    exercise_name,
    total_reps,
    good_form_reps=None,
    duration_sec=None,
):
    """
    Tạo nhận xét tổng kết sau buổi tập cho trang Summary.
    """
    if total_reps <= 0:
        return (
            f"Bạn chưa hoàn thành nhịp {exercise_name} nào. "
            "Hãy kiểm tra lại góc camera để thấy toàn thân và thử lại nhé!"
        )

    summary_parts = [f"Bạn đã hoàn thành {total_reps} rep {exercise_name}."]

    if good_form_reps is not None and total_reps > 0:
        accuracy = (good_form_reps / total_reps) * 100
        if accuracy >= 85:
            summary_parts.append(f"Độ chuẩn kỹ thuật đạt {accuracy:.0f}% — Tư thế rất vững và ổn định!")
        elif accuracy >= 60:
            summary_parts.append(f"Độ chuẩn kỹ thuật đạt {accuracy:.0f}% — Khá tốt, hãy chú ý hạ sâu và giữ thẳng lưng hơn ở các nhịp cuối.")
        else:
            summary_parts.append(f"Độ chuẩn kỹ thuật đạt {accuracy:.0f}% — Nên tập chậm lại để kiểm soát biên độ động tác chuẩn xác hơn.")

    if duration_sec is not None and duration_sec > 0:
        pace = total_reps / (duration_sec / 60.0)
        summary_parts.append(f"Tốc độ trung bình: {pace:.1f} rep/phút.")

    return " ".join(summary_parts)


def build_feedback_payload(message, level="normal", issue_code=None):
    """
    Đóng gói dữ liệu phản hồi có kèm phân loại màu sắc cho giao diện Web.
    level: "good" (xanh), "warning" (vàng), "error" (đỏ), "normal" (trung tính).
    """
    return {
        "message": message,
        "level": level,
        "issue_code": issue_code,
    }