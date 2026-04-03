<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈氏家族 - 首页</title>
    <style>
        body {
            font-family: 'SimSun', serif;
            margin: 0;
            padding: 0;
            background-color: #f4e9ce;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...');
            background-repeat: repeat;
            color: #5b4636;
        }
        
        .header {
            background-color: #5b4636;
            color: #f4e9ce;
            padding: 15px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 100;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #f4e9ce;
            text-decoration: none;
            display: flex;
            align-items: center;
        }
        
        .logo img {
            height: 40px;
            margin-right: 10px;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .nav-menu li {
            margin-left: 30px;
        }
        
        .nav-menu a {
            color: #f4e9ce;
            text-decoration: none;
            font-size: 18px;
            padding: 5px 10px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        
        .nav-menu a:hover, .nav-menu a.active {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .page-title {
            text-align: center;
            color: #5b4636;
            font-size: 48px;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            animation: fadeInTitle 2s ease-in-out;
            padding: 0 20px;
        }
        
        .search-container {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
        }
        
        .search-icon {
            cursor: pointer;
            width: 24px;
            height: 24px;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>');
            background-size: cover;
            margin-right: 15px;
        }
        
        .search-input {
            display: none;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            width: 200px;
            margin-top: 10px;
        }
        
        .birthday-notice {
            background-color: #fff9e6;
            border: 1px solid #ffd700;
            border-radius: 5px;
            padding: 10px 15px;
            margin-top: 10px;
            display: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-width: 300px;
        }
        
        .birthday-notice.show {
            display: block;
        }
        
        .birthday-title {
            font-weight: bold;
            color: #e67e22;
            margin-bottom: 5px;
        }
        
        .birthday-name {
            color: #5b4636;
        }
        
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin: 70px auto 30px;
            max-width: 1200px;
            padding: 0 20px;
        }
        
        a.member-link {
            display: block;
            text-decoration: none;
            color: #7f5f3f;
            padding: 15px;
            margin: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            width: calc(33.33% - 20px);
            text-align: center;
            font-size: 18px;
            transition: all 0.3s ease;
        }
        
        a.member-link:hover {
            background-color: #e9ecef;
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        @keyframes fadeInTitle {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .footer {
            background-color: #5b4636;
            color: #f4e9ce;
            text-align: center;
            padding: 20px;
            margin-top: 50px;
        }
        
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                padding: 10px;
            }
            
            .logo {
                margin-bottom: 10px;
            }
            
            .nav-menu {
                width: 100%;
                justify-content: space-around;
            }
            
            .nav-menu li {
                margin: 0;
            }
            
            .page-title {
                font-size: 36px;
                margin: 20px 0;
            }
            
            .search-container {
                position: static;
                margin: 10px auto;
                text-align: center;
                justify-content: center;
            }
            
            a.member-link {
                width: calc(50% - 20px);
            }
        }
        
        @media (max-width: 480px) {
            a.member-link {
                width: 100%;
            }
            
            .birthday-notice {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="index.php" class="logo">
                陈氏家族
            </a>
            <ul class="nav-menu">
                <li><a href="index.php" class="active">首页</a></li>
                <li><a href="ls.html">家族历史</a></li>
                <li><a href="zp3.php">关系图谱</a></li>
                <li><a href="lt.html">家族论坛</a></li>
            </ul>
        </div>
    </header>

    <h1 class="page-title">陈氏家族成员名单</h1>
    
    <div class="search-container">
        <div class="search-icon"></div>
        <input type="text" id="searchInput" class="search-input" placeholder="按姓名查找...">
        
        <?php
        // 农历生日提醒功能
        $servername = "mysql.sqlpub.com:3306";
        $username = "cgf0727";
        $password = "kruZIfw9j5CYIetU";
        $dbname = "xcp1254";
        
        // 创建数据库连接
        $conn = new mysqli($servername, $username, $password, $dbname);
        
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }
        
        // 获取当前日期
        $current_date = date('Y-m-d');
        
        // 简单模拟农历日期（实际项目中应使用专门的农历计算库）
        // 这里假设数据库中的"农历生日"字段存储的是"MM-DD"格式的字符串
        $sql = "SELECT 姓名 FROM 陈 WHERE DATE_FORMAT(STR_TO_DATE(生日, '%m月%d'), '%m月%d') = DATE_FORMAT(NOW(), '%m-%d')";
        $result = $conn->query($sql);
        
        $birthday_names = array();
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $birthday_names[] = $row["姓名"];
            }
        }
        
        // 关闭连接
        $conn->close();
        
        // 显示生日提醒
        if (!empty($birthday_names)) {
            echo '<div class="birthday-notice show">';
            echo '<div class="birthday-title">🎂 今天过生日的家人:</div>';
            echo '<div class="birthday-name">' . implode('、', $birthday_names) . '</div>';
            echo '</div>';
        } else {
            echo '<div class="birthday-notice"></div>';
        }
        ?>
    </div>
    
    <div class="container" id="familyContainer">
        <?php
        // 重新建立数据库连接获取成员列表
        $conn = new mysqli($servername, $username, $password, $dbname);
        
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }
        
        $sql = "SELECT ID, 姓名 FROM 陈 ORDER BY 出生年份 ASC";
        $result = $conn->query($sql);
        
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<a href='cgf2.php?id=" . htmlspecialchars($row["ID"]) . "' class='member-link' data-name='" . htmlspecialchars($row["姓名"]) . "'>" . htmlspecialchars($row["姓名"]) . "</a>";
            }
        } else {
            echo "<p>暂无家族成员数据</p>";
        }
        
        $conn->close();
        ?>
    </div>

    <footer class="footer">
        <p>© 2025 陈氏家族 版权所有</p>
    </footer>

    <script>
        document.querySelector('.search-icon').addEventListener('click', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput.style.display === 'none' || searchInput.style.display === '') {
                searchInput.style.display = 'inline-block';
                searchInput.focus();
            } else {
                searchInput.style.display = 'none';
            }
        });

        document.getElementById('searchInput').addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const links = document.querySelectorAll('#familyContainer a.member-link');

            links.forEach(link => {
                const name = link.getAttribute('data-name').toLowerCase();
                if (name.includes(filter)) {
                    link.style.display = '';
                } else {
                    link.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>