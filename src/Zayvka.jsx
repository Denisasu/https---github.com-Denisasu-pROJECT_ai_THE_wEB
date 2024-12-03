import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Form, Image, Alert } from 'react-bootstrap';
import avatar from './imgs/login/avatar.svg';
import wave from './imgs/login/wave.png';
import bg from './imgs/login/bg.svg';

import styles from './Zayvka.module.css';

function Zayvka() {
    const [image, setImage] = useState(null);
    const [email, setEmail] = useState('');
    const [longitude, setLongitude] = useState('');
    const [latitude, setLatitude] = useState('');
    const [description, setDescription] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showAlert, setShowAlert] = useState(false);
    const [focused, setFocused] = useState({});

    useEffect(() => {
        navigator.geolocation.getCurrentPosition((position) => {
            const { latitude, longitude } = position.coords;
            setLongitude(longitude.toFixed(4));
            setLatitude(latitude.toFixed(4));
        });
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsSubmitting(true);

        if (!image) {
            console.error('Файл изображения не выбран');
            setIsSubmitting(false);
            return;
        }

        const reader = new FileReader();
        reader.readAsDataURL(image);
        reader.onloadend = async () => {
            const base64Image = reader.result.split(',')[1];

            const applicationData = {
                photo: base64Image,
                email: email,
                longitude: parseFloat(longitude),
                latitude: parseFloat(latitude),
                description: description,
            };

            try {
                const response = await axios.post('http://localhost:8000/applications/', applicationData, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                console.log('Заявка успешно отправлена:', response.data);
                setIsSubmitting(false);
                setShowAlert(true);
                setImage(null);
                setEmail('');
                setDescription('');
            } catch (error) {
                console.error('Ошибка при отправке заявки:', error.response?.data || error);
                setIsSubmitting(false);
            }
        };
    };

    const handleFocus = (field) => {
        setFocused((prevState) => ({ ...prevState, [field]: true }));
    };

    const handleBlur = (field, value) => {
        if (!value) {
            setFocused((prevState) => ({ ...prevState, [field]: false }));
        }
    };

    const handleImageChange = (event) => {
        const file = event.target.files[0];
        setImage(file);
    };

    const handleCloseAlert = () => {
        setShowAlert(false);
    };

    return (
        <div className={styles.zayvkaContainer}>
            <img src={wave} className={styles.wave} alt="wave" />
            <div className={styles.container}>
                <div className={styles.img}>
                    <img src={bg} alt="background" />
                </div>
                <div className={styles.zayvkaContent}>
                    <Alert
                        variant="success"
                        show={showAlert}
                        onClose={handleCloseAlert}
                        dismissible
                        className={styles.alert}
                    >
                        Заявка успешно отправлена! Ваша заявка очень важна для нас, вместе мы очистим природу от мусора!
                    </Alert>

                    <form onSubmit={handleSubmit} encType="multipart/form-data">
                        <div className={styles.avatarWrapper}>
                            <img src={avatar} alt="avatar" className={styles.avatar} />
                        </div>
                        <h2 className={styles.title}>Заявка</h2>

                        <div className={`${styles.inputDiv} ${focused.photo ? styles.focus : ''}`}>
                            <div className={styles.icon}>
                                <i className="fas fa-camera"></i>
                            </div>
                            <div className={styles.inputWrapper}>
                                <h5>Фото</h5>
                                <input
                                    type="file"
                                    onChange={handleImageChange}
                                    className={styles.input}
                                    accept=".jpg, .jpeg, .png"
                                />
                            </div>
                        </div>

                        {image && (
                            <div className={styles.preview}>
                                <Image src={URL.createObjectURL(image)} fluid />
                            </div>
                        )}

                        <div className={`${styles.inputDiv} ${focused.email ? styles.focus : ''}`}>
                            <div className={styles.icon}>
                                <i className="fas fa-user"></i>
                            </div>
                            <div className={styles.inputWrapper}>
                                <h5>Email</h5>
                                <input
                                    type="email"
                                    className={styles.input}
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onFocus={() => handleFocus('email')}
                                    onBlur={(e) => handleBlur('email', e.target.value)}
                                />
                            </div>
                        </div>

                        <div className={styles.locationWrapper}>
                            <div>
                                <h5>Широта</h5>
                                <input type="text" value={latitude} readOnly className={styles.input} />
                            </div>
                            <div>
                                <h5>Долгота</h5>
                                <input type="text" value={longitude} readOnly className={styles.input} />
                            </div>
                        </div>

                        <div className={`${styles.inputDiv} ${focused.description ? styles.focus : ''}`}>
                            <div className={styles.icon}>
                                <i className="fas fa-pencil-alt"></i>
                            </div>
                            <div className={styles.inputWrapper}>
                                <h5>Описание заявки</h5>
                                <textarea
                                    className={styles.input}
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    onFocus={() => handleFocus('description')}
                                    onBlur={(e) => handleBlur('description', e.target.value)}
                                />
                            </div>
                        </div>

                        <div className={styles.buttonsWrapper}>
                            <button
                                type="submit"
                                className={`${styles.btn} ${isSubmitting ? styles.submitting : ''}`}
                                disabled={isSubmitting || !email || !longitude || !latitude || !description || !image}
                            >
                                {isSubmitting ? 'Отправка...' : 'Отправить заявку'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Zayvka;
