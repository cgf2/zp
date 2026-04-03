<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>陈氏家族成员资料</title>
    <style>
        body {
            font-family: 'SimSun', serif;
            margin: 0;
            padding: 20px;
            background-color: #f4e9ce; /* 背景颜色改为米黄色 */
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIA...'); /* 添加背景纹理 */
            background-repeat: repeat;
        }
        h1 {
            text-align: center;
            color: #5b4636; /* 字体颜色改为深棕色 */
            font-size: 36px; /* 增加字体大小 */
            margin-top: 20px;
        }
        .family-title {
            text-align: center;
            color: #7f5f3f; /* 标题颜色改为更深的棕色 */
            font-size: 48px; /* 更大的字体大小 */
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* 添加阴影效果 */
        }
        .product-details {
            max-width: 600px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.8); /* 半透明白色背景 */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            animation: fadeIn 1s ease-in-out;
            position: relative; /* 相对定位 */
        }
        .product-details p {
            margin-bottom: 10px;
            line-height: 1.6;
            color: #333;
        }
        .product-details strong {
            color: #7f5f3f; /* 加粗字体颜色改为深棕色 */
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin-bottom: 5px;
        }
        a {
            color: #7f5f3f; /* 链接颜色改为深棕色 */
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            h1 {
                font-size: 30px;
            }
            .family-title {
                font-size: 36px;
            }
            .product-details {
                padding: 15px;
            }
            .product-details p {
                font-size: 20px;
            }
        }
        .image-box {
            width: 130px;
            height: 180px;
            overflow: hidden;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            position: absolute; /* 绝对定位 */
            top: 20px; /* 距离顶部20px */
            right: 20px; /* 距离右侧20px */
        }
        .image-box img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
    </style>
</head>
<body>
    <h1 class="family-title">陈氏家族</h1>

    <?php
    // 数据库配置信息
    $servername = "mysql.sqlpub.com:3306";
    $username = "cgf0727";
    $password = "kruZIfw9j5CYIetU";
    $dbname = "xcp1254";

    // 创建连接
    $conn = new mysqli($servername, $username, $password, $dbname);

    // 设置字符集为utf8mb4
    $conn->set_charset("utf8mb4");

    // 检查连接
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    // 获取URL中的ID参数
    if (isset($_GET['id'])) {
        $id = intval($_GET['id']);

        // 使用预处理语句防止SQL注入
        $stmt = $conn->prepare("SELECT * FROM 陈 WHERE ID = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            echo "<div class='product-details'>"; 
            // 输出数据
            while($row = $result->fetch_assoc()) {
                $name = htmlspecialchars($row["姓名"]);
                $image = htmlspecialchars($row["图片"]); // 假设有图片字段
                $birthYear = intval($row["出生年份"]);
                $birthday = htmlspecialchars($row["生日"]);
                $deathYear = intval($row["终年"]);
                $spouse = htmlspecialchars($row["配偶"]);
                $contact = htmlspecialchars($row["联系方式"]); // 新增获取联系方式
                $daughter = htmlspecialchars($row["女儿"]);
                $fxid = intval($row["父亲ID"]);

                // 计算年龄或终年
                $ss = "";
                if ($deathYear == 0) {
                    $currentYear = date('Y');
                    $age = $currentYear - $birthYear + 1; // 增加1岁以符合实际年龄计算
                    $ageDisplay = $age . " 岁";
                    $ss = "年龄";
                } else {
                    $ageDisplay = ($deathYear - $birthYear + 1) . " 岁";
                    $ss = "终年";
                }

                // 计算生肖
                $zodiacAnimals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"];
                $zodiacIndex = ($birthYear - 1300) % 12;
                $zodiacAnimal = $zodiacAnimals[$zodiacIndex];
                
                if (!empty($image)) {
                    echo "<div class='image-box'><img src='" . $image . "' alt='" . $name . "'></div>"; // 输出图片
                }

                echo "<h2>" . $name . "</h2>"; // 输出姓名
                echo "<p><strong>出生年份:</strong> " . $birthYear . "</p>"; // 输出出生年份
                echo "<p><strong>生日:</strong> " . $birthday . "</p>"; // 输出生日
                echo "<p><strong>$ss:</strong> " . $ageDisplay . "</p>"; // 输出年龄或终年
                echo "<p><strong>生肖:</strong> " . $zodiacAnimal . "</p>"; // 输出生肖

                // 如果有联系方式，则输出
                if (!empty($contact)) {
                    echo "<p><strong>联系方式:</strong> " . $contact . "</p>";
                }

                echo "<p><strong>配偶:</strong> " . $spouse . "</p>";
                echo "<p><strong>女儿:</strong> " . $daughter . "</p>";

                // 查询父亲信息
                $stmt_father = $conn->prepare("SELECT * FROM 陈 WHERE ID = ?");
                $stmt_father->bind_param("i", $fxid);
                $stmt_father->execute();
                $result_father = $stmt_father->get_result();

                if ($result_father->num_rows > 0) {
                    $father = $result_father->fetch_assoc();
                    echo "<p><strong>父亲:</strong> <a href='cgf2.php?id=".htmlspecialchars($father["ID"])."'>" . htmlspecialchars($father["姓名"]) ."</a></p>";
                } else {
                    echo "<p><strong>父亲:</strong> 未知</p>";
                }
                // 关闭父查询语句
                $stmt_father->close();
                // 查询兄弟信息（包括当前记录）
                $stmt_xd = $conn->prepare("SELECT * FROM 陈 WHERE 父亲ID = ? ORDER BY 出生年份");
                $stmt_xd->bind_param("i", $fxid);
                $stmt_xd->execute();
                $result_xd = $stmt_xd->get_result();
                if ($result_xd->num_rows > 0) {
                    echo "<p><strong>兄弟:</strong> <a href='cgf3.php?id=$id'>排行</a> </p>";
                    echo "<ul>";
                    $brotherOrder = ["老大", "老二", "老三", "老四", "老五", "老六", "老七", "老八", "老九", "老十"];
                    $index = 0;
                    while ($brother = $result_xd->fetch_assoc()) {
                        echo "<li><strong>" . $brotherOrder[$index] . ":</strong> <a href='cgf2.php?id=".htmlspecialchars($brother["ID"])."'>" . htmlspecialchars($brother["姓名"]) . "</a></li>";
                        $index++;
                    }
                    echo "</ul>";
                } else {
                    echo "<p><strong>兄弟:</strong> 未知</p>";
                }

                // 关闭兄弟查询语句
                $stmt_xd->close();

                // 查询儿子信息（基于当前ID）
                $stmt_zn = $conn->prepare("SELECT * FROM 陈 WHERE 父亲ID = ? ORDER BY 出生年份");
                $stmt_zn->bind_param("i", $id);
                $stmt_zn->execute();
                $result_zn = $stmt_zn->get_result();

                if ($result_zn->num_rows > 0) {
                    echo "<p><strong>儿子:</strong></p>";
                    echo "<ul>";
                    $sonOrder = ["长子", "次子", "三子", "四子", "五子", "六子", "七子", "八子", "九子", "十子"];
                    $index = 0;
                    while ($son = $result_zn->fetch_assoc()) {
                        echo "<li><strong>" . $sonOrder[$index] . ":</strong> <a href='cgf2.php?id=".htmlspecialchars($son["ID"])."'>" . htmlspecialchars($son["姓名"]) . "</a></li>";
                        $index++;
                    }
                    echo "</ul>";
                } else {
                    echo "<p><strong>儿子:</strong> 未知</p>";
                }

                // 关闭儿子查询语句
                $stmt_zn->close();
            }
            echo "</div>"; 
        } else {
            echo "<p>No product found with ID: " . htmlspecialchars($id) . "</p>";
        }

        // 关闭主查询语句
        $stmt->close();
    } else {
        echo "<p>ID parameter is missing.</p>";
    }

    // 关闭连接
    $conn->close();
    ?>
</body>
</html>


