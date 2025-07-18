// /Users/apichet/Downloads/cheetah-insurance-app/src/components/ProfilePicture.jsx
// /src/components/ProfilePicture.jsx
// /src/components/ProfilePicture.jsx
import React, { memo, useState, useMemo, useCallback, useEffect } from "react";
import PropTypes from "prop-types";
import { resolveProfileImage } from "../utils/imageUtils";

const DEFAULT_IMAGE = "/images/default-profile.png?v=1";
const MAX_FILE_SIZE_MB = 5;

const ProfilePicture = memo(({ profilePictureUrl, handleUploadProfilePicture, profilePictureUploading }) => {
  const [previewURL, setPreviewURL] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    return () => {
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
  }, [previewURL]);

  const currentImage = useMemo(() => {
    if (previewURL) return previewURL;
    return resolveProfileImage(profilePictureUrl);
  }, [previewURL, profilePictureUrl]);

  const handleImageError = useCallback((e) => {
    console.warn("⚠️ โหลดรูปไม่สำเร็จ ใช้ default แทน");
    e.target.onerror = null;
    e.target.src = DEFAULT_IMAGE;
  }, []);

  const handleFileChange = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setErrorMessage("กรุณาเลือกไฟล์รูปภาพเท่านั้น");
      return;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setErrorMessage(`ขนาดไฟล์เกิน ${MAX_FILE_SIZE_MB}MB`);
      return;
    }

    setErrorMessage("");
    const preview = URL.createObjectURL(file);
    setPreviewURL(preview);
    handleUploadProfilePicture(file);
  }, [handleUploadProfilePicture]);

  return (
    <div style={styles.container}>
      <svg width="0" height="0">
        <defs>
          <clipPath id="squircle" clipPathUnits="objectBoundingBox">
            <path d="M0.5,0 C0.90,0 1,0.09 1,0.5 C1,0.91 0.9,1 0.5,1 C0.09,1 0,0.9 0,0.5 C0,0.09 0.09,0 0.5,0Z" />
          </clipPath>
        </defs>
      </svg>

      <div style={styles.avatarWrapper}>
        <img
          src={currentImage}
          alt="Profile"
          onError={handleImageError}
          onLoad={() => console.log("📷 Loaded:", currentImage)}
          style={styles.squircleImage}
        />
      </div>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={profilePictureUploading}
        style={styles.input}
      />
      {profilePictureUploading && <p style={styles.uploading}>⏳ กำลังอัปโหลด...</p>}
      {errorMessage && <p style={styles.error}>⚠️ {errorMessage}</p>}
    </div>
  );
});

ProfilePicture.propTypes = {
  profilePictureUrl: PropTypes.string,
  handleUploadProfilePicture: PropTypes.func.isRequired,
  profilePictureUploading: PropTypes.bool,
};

ProfilePicture.defaultProps = {
  profilePictureUrl: null,
  profilePictureUploading: false,
};

const styles = {
  container: {
    textAlign: "center",
    marginTop: "20px",
  },
  avatarWrapper: {
    width: "150px",
    aspectRatio: "1",
    margin: "0 auto",
  },
  squircleImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    clipPath: "url(#squircle)",
    backgroundColor: "#eee",
  },
  input: {
    display: "block",
    margin: "0 auto",
    marginTop: "10px",
  },
  uploading: {
    color: "#ff9800",
    marginTop: "10px",
  },
  error: {
    color: "red",
    marginTop: "8px",
  },
};

export default ProfilePicture;
