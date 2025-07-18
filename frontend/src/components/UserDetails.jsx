/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/UserDetails.jsx */
// /src/components/UserDetails.jsx
import React from "react";
import PropTypes from "prop-types";

// 🔧 แยกย่อยเพื่อให้รองรับ UI เพิ่มเติมในอนาคต
const InfoRow = ({ label, value, onEdit, editLabel }) => (
  <p>
    <strong>{label}:</strong> {value || "-"}
    {onEdit && (
      <button className="edit-button" onClick={onEdit} aria-label={`Edit ${label}`}>
        ✏️ {editLabel || "แก้ไข"}
      </button>
    )}
  </p>
);

InfoRow.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string,
  onEdit: PropTypes.func,
  editLabel: PropTypes.string,
};

const UserDetails = React.memo(({ user, handleUpdatePhoneNumber, handleEditProfile }) => {
  if (!user) {
    return <p>⏳ กำลังโหลดข้อมูลผู้ใช้...</p>;
  }

  const { customer, user: userData } = user;

  return (
    <div className="user-details">
      <InfoRow label="ชื่อ" value={`${customer?.first_name || "-"} ${customer?.last_name || "-"}`} />
      <InfoRow label="อีเมล" value={userData?.email} />
      <InfoRow
        label="เบอร์โทรศัพท์"
        value={customer?.phone_number || "ยังไม่ได้ระบุ"}
        onEdit={handleUpdatePhoneNumber}
      />
      <InfoRow label="ที่อยู่" value={customer?.address || "ยังไม่ได้ระบุ"} />

      {handleEditProfile && (
        <button className="edit-button" onClick={handleEditProfile} aria-label="Edit Profile">
          ✏️ แก้ไขโปรไฟล์
        </button>
      )}
    </div>
  );
});

UserDetails.propTypes = {
  user: PropTypes.shape({
    user: PropTypes.shape({
      email: PropTypes.string,
    }),
    customer: PropTypes.shape({
      first_name: PropTypes.string,
      last_name: PropTypes.string,
      phone_number: PropTypes.string,
      address: PropTypes.string,
    }),
  }),
  handleUpdatePhoneNumber: PropTypes.func,
  handleEditProfile: PropTypes.func,
};

export default UserDetails;
