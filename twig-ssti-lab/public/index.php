<?php
declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

use Twig\Environment;
use Twig\Loader\FilesystemLoader;
use Twig\TwigFunction;

// Loader trỏ về /var/www/html/templates
$loader = new FilesystemLoader(__DIR__ . '/../templates');
$twig = new Environment($loader, ['autoescape' => 'html']);

//function nguy hiểm để thấy RCE khi SSTI
$twig->addFunction(new TwigFunction('exec', 'shell_exec'));

// Chặn reflected XSS
function escape_angle(string $s): string {
  return str_replace(['<','>'], ['&lt;','&gt;'], $s);
}

// Input
$q = $_POST['q'] ?? $_GET['q'] ?? '';

// LỖ HỔNG: render template từ CHUỖI có nhúng trực tiếp input
$vulnerableTemplate = <<<TWIG
{% extends "base.html.twig" %}
{% block content %}
  <h2>Nhập username</h2>
  <form method="post" action="/index.php">
    <input type="text" name="q" value="{{ q|e }}" placeholder="Nhập username của bạn ở đây…">
    <button type="submit">Gửi</button>
  </form>

  <div class="card">
    <strong>Xin chào: %PAYLOAD%</strong>
  </div>
{% endblock %}
TWIG;

// Không WAF: luôn chèn payload
$vulnerableTemplate = str_replace('%PAYLOAD%', escape_angle($q), $vulnerableTemplate);

// Render từ CHUỖI template có SSTI
echo $twig->createTemplate($vulnerableTemplate)->render(['q' => $q]);
