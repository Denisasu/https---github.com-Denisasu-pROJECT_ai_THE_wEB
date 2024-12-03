import { Container, Nav, Navbar } from 'react-bootstrap';
import logo from '../../imgs/glavlog.png';
import userlogo from '../../imgs/Vector.png';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../pages/AuthContext'; // Подключаем контекст аутентификации
import 'bootstrap/dist/css/bootstrap.min.css';

function Header() {
  const navigate = useNavigate();
  const { user } = useAuth(); // Получаем данные пользователя из контекста

  const handleIconClick = () => {
    if (user) {
      // Если пользователь авторизован, переходим в личный кабинет
      navigate('/personalacc');
    } else {
      // Если пользователь не авторизован, переходим на страницу входа
      navigate('/login');
    }
  };

  return (
    <Navbar fixed="top" collapseOnSelect expand="md" style={{ backgroundColor: '#38D39F', color: '#D0D0D0', height: '45px' }}>
      <Container>
        <Navbar.Brand as={Link} to="/" style={{ display: 'flex', alignItems: 'center' }}>
          <img src={logo} height={40} width={40} alt="Logo" />
          <span style={{ paddingLeft: '10px' }}>Защитник природы</span>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav" />
        <Navbar.Collapse id="responsive-navbar-nav" style={{ flexDirection: 'row-reverse' }}>
          <Nav className="mr-auto">
            <Nav.Link as={Link} to="/">Главная</Nav.Link>
            <Nav.Link as={Link} to="/statistics">Статистика</Nav.Link>
            <Nav.Link as={Link} to="/contacts">Контакты</Nav.Link>
            <Nav.Link as={Link} to="/analyze">Анализ</Nav.Link>
            <Nav.Link as={Link} to="/zayvka">Заявка</Nav.Link>
          </Nav>
        </Navbar.Collapse>
        <img
          src={userlogo}
          height={30}
          width={30}
          alt="UserLogo"
          style={{ cursor: 'pointer', marginLeft: '15px' }}
          onClick={handleIconClick} // Вызываем функцию при клике на иконку
        />
      </Container>
    </Navbar>
  );
}

export default Header;
