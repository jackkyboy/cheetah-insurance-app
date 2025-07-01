// /Users/apichet/Downloads/cheetah-insurance-app/src/components/ProfilePicture.jsx
// /src/components/ProfilePicture.jsx
import React, { memo, useEffect, useState, useCallback } from "react";
import PropTypes from "prop-types";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:5000";
const DEFAULT_IMAGE = "/api/static/images/default-profile.png";
const MAX_FILE_SIZE_MB = 5;

const buildImageUrl = (path) => {
  if (!path) return DEFAULT_IMAGE;
  if (path.startsWith("http")) return path;
  if (path.startsWith("/api")) return `${API_BASE_URL.replace(/\/api$/, "")}${path}`;
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
};

const ProfilePicture = memo(({ profilePictureUrl, handleUploadProfilePicture, profilePictureUploading }) => {
  const [currentImage, setCurrentImage] = useState(DEFAULT_IMAGE);
  const [previewURL, setPreviewURL] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    return () => {
      if (previewURL) URL.revokeObjectURL(previewURL);
    };
  }, [previewURL]);

  useEffect(() => {
    setCurrentImage(
      previewURL
        ? previewURL
        : profilePictureUrl
        ? buildImageUrl(profilePictureUrl)
        : DEFAULT_IMAGE
    );
  }, [profilePictureUrl, previewURL]);

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
    setCurrentImage(preview);
    handleUploadProfilePicture(file);
  }, [handleUploadProfilePicture]);

  return (
    <div style={styles.container}>
      {/* 🔶 Squircle Definition */}
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
