
def get_squat_feedback(angle, state):
    """
    Phản hồi cho bài tập Squat.
    """

    if angle is None:
        return "Không nhận diện được góc đầu gối."

    if state == "STANDING":
        return "Tư thế đứng ổn định. Tiếp tục thực hiện động tác."

    elif state == "DESCENDING":
        if angle > 120:
            return "Hãy tiếp tục hạ thấp cơ thể."
        return "Đang hạ người tốt. Cố gắng giữ lưng ổn định."

    elif state == "BOTTOM":
        return "Đã đạt vị trí Squat. Bây giờ hãy đứng lên."

    elif state == "ASCENDING":
        return "Đang đứng lên. Hãy duỗi chân để hoàn thành động tác."

    return "Tiếp tục thực hiện Squat."


def get_jumping_jack_feedback(
    arms_up,
    leg_ratio,
    state,
    open_leg_ratio=1.5
):
    """
    Phản hồi cho bài tập Jumping Jack.
    """

    if leg_ratio is None:
        return "Không nhận diện được vị trí chân."

    if state == "CLOSED":
        if arms_up:
            return "Hãy khép chân và đưa hai tay xuống."

        if leg_ratio > 1.15:
            return "Hãy khép hai chân lại."

        return "Tư thế sẵn sàng. Hãy bật nhảy mở tay và chân."

    elif state == "OPEN":
        if not arms_up:
            return "Hãy giơ hai tay cao hơn vai."

        if leg_ratio < open_leg_ratio:
            return "Hãy mở rộng hai chân hơn."

        return "Tư thế mở tốt. Hãy khép tay và chân lại."

    return "Tiếp tục thực hiện Jumping Jack."


def get_general_feedback(valid):
    """
    Phản hồi chung về khả năng nhận diện cơ thể.
    """

    if not valid:
        return "Vui lòng đứng ở vị trí camera có thể nhận diện rõ cơ thể."

    return "Đang theo dõi chuyển động."
