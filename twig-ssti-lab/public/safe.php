<?php
declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

use Twig\Environment;
use Twig\Loader\FilesystemLoader;

$loader = new FilesystemLoader(__DIR__ . '/../templates');
$twig = new Environment($loader, ['autoescape' => 'html']);

$q = $_GET['q'] ?? '';
echo $twig->render('safe.html.twig', ['q' => $q]);  // template cố định -> không SSTI
