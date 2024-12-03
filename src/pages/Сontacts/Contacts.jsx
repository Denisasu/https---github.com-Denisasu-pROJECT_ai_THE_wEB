import React, { useState } from 'react';
import { Form, Alert } from 'react-bootstrap';
import avatar from '../../imgs/login/avatar.svg';
import wave from '../../imgs/login/wave.png';
import bg from '../../imgs/login/bg.svg';
import styles from './Contacts.module.css';

function Contacts() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [agreementChecked, setAgreementChecked] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  const [focused, setFocused] = useState({});

  const handleFocus = (field) => {
    setFocused((prevState) => ({ ...prevState, [field]: true }));
  };

  const handleBlur = (field, value) => {
    if (!value) {
      setFocused((prevState) => ({ ...prevState, [field]: false }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!agreementChecked) return;

    const feedbackData = { email, name, message: description };

    setIsSubmitting(true);

    try {
      const response = await fetch('http://localhost:8000/messages/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData),
      });

      if (!response.ok) throw new Error('Ошибка при отправке сообщения');
      setIsSubmitting(false);
      setShowSuccessAlert(true);
    } catch (error) {
      console.error('Ошибка:', error);
      setIsSubmitting(false);
    }
  };

  const handleCheckboxChange = () => {
    setAgreementChecked(!agreementChecked);
  };

  const handleCloseAlert = () => {
    setShowSuccessAlert(false);
  };

  return (
    <div className={styles.contactsContainer}>
      <img src={wave} className={styles.wave} alt="wave" />
      <div className={styles.container}>
        <div className={styles.img}>
          <img src={bg} alt="background" />
        </div>
        <div className={styles.contactsContent}>
          <Alert
            variant="success"
            show={showSuccessAlert}
            onClose={handleCloseAlert}
            dismissible
            className={styles.alert}
          >
            Обратная связь успешно отправлена!
          </Alert>

          <form onSubmit={handleSubmit} encType="multipart/form-data">
            <div className={styles.avatarWrapper}>
              <img src={avatar} alt="avatar" className={styles.avatar} />
            </div>
            <h2 className={styles.title}>Обратная связь</h2>

            <div className={`${styles.inputDiv} ${focused.name ? styles.focus : ''}`}>
              <div className={styles.icon}>
                <i className="fas fa-user"></i>
              </div>
              <div className={styles.inputWrapper}>
                <h5>ФИО</h5>
                <input
                  type="text"
                  className={styles.input}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  onFocus={() => handleFocus('name')}
                  onBlur={(e) => handleBlur('name', e.target.value)}
                />
              </div>
            </div>

            <div className={`${styles.inputDiv} ${focused.email ? styles.focus : ''}`}>
              <div className={styles.icon}>
                <i className="fas fa-envelope"></i>
              </div>
              <div className={styles.inputWrapper}>
                <h5>Электронная почта</h5>
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

            <div className={`${styles.inputDiv} ${focused.question ? styles.focus : ''}`}>
              <div className={styles.icon}>
                <i className="fas fa-pencil-alt"></i>
              </div>
              <div className={styles.inputWrapper}>
                <h5>Ваш вопрос</h5>
                <textarea
                  className={styles.input}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  onFocus={() => handleFocus('question')}
                  onBlur={(e) => handleBlur('question', e.target.value)}
                />
              </div>
            </div>

            <div className={styles.checkboxWrapper}>
              <input
                type="checkbox"
                checked={agreementChecked}
                onChange={handleCheckboxChange}
              />
              <span className={styles.agreementText}>
                Я согласен с условиями обработки персональных данных
              </span>
            </div>

            <div className={styles.buttonsWrapper}>
              <button
                type="submit"
                className={`${styles.btn} ${isSubmitting ? styles.submitting : ''}`}
                disabled={isSubmitting || !email || !name || !description}
              >
                {isSubmitting ? 'Отправка...' : 'Отправить'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Contacts;
