/*/Users/apichet/Downloads/cheetah-insurance-app/src/components/UserDetails.jsx */
import React from "react";

// Component for displaying and editing user details
const UserDetails = ({
  user,
  handleUpdatePhoneNumber,
  handleEditProfile,
}) => {
  if (!user) {
    return <p>⏳ กำลังโหลดข้อมูลผู้ใช้...</p>; // Handle case when user data is not yet loaded
  }

  return (
    <div className="user-details">
      {/* Display User Name */}
      <p>
        <strong>ชื่อ:</strong> {user.customer?.first_name || "-"} {user.customer?.last_name || "-"}
      </p>

      {/* Display User Email */}
      <p>
        <strong>อีเมล:</strong> {user.user?.email || "-"}
      </p>

      {/* Display User Phone Number with Edit Button */}
      <p>
        <strong>เบอร์โทรศัพท์:</strong> {user.customer?.phone_number || "ยังไม่ได้ระบุ"}
        {handleUpdatePhoneNumber && (
          <button
            className="edit-button"
            onClick={handleUpdatePhoneNumber}
            aria-label="Edit Phone Number"
          >
            ✏️ แก้ไข
          </button>
        )}
      </p>

      {/* Display User Address */}
      <p>
        <strong>ที่อยู่:</strong> {user.customer?.address || "ยังไม่ได้ระบุ"}
      </p>

      {/* Edit Profile Button */}
      {handleEditProfile && (
        <button
          className="edit-button"
          onClick={handleEditProfile}
          aria-label="Edit Profile"
        >
          ✏️ แก้ไขโปรไฟล์
        </button>
      )}
    </div>
  );
};

export default UserDetails;
