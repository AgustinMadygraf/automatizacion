<?php
// automatizacion/app/controllers/get_data.php

error_reporting(E_ALL);
ob_start();

require_once '../../vendor/autoload.php';
include '../services/DatabaseConnection.php';
include '../services/ConfigChecker.php';
include '../services/DataFetcher.php';

ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/../../logs/error_log.txt');

// header para JSON
header('Content-Type: application/json');

try {
    // Instancia de ConfigChecker
    $configChecker = new ConfigChecker('../../.env');
    if (!$configChecker->check()) {
        ob_end_clean();
        echo json_encode([
            'error' => true,
            'message' => 'Falta el archivo de configuración',
            'details' => 'El archivo .env no se encuentra en la ruta esperada. Redirigiendo a la instalación.'
        ]);
        exit();
    }

    // Conexión a la base de datos
    $dbConnection = new DatabaseConnection();
    $conn = $dbConnection->getConnection();

    // Obtener datos
    $dataFetcher = new DataFetcher($conn);
    $data = $dataFetcher->fetchLatestData();

    $dbConnection->close();

    ob_end_clean();
    echo json_encode(['error' => false, 'data' => $data]);

} catch (Exception $e) {
    ob_end_clean();
    error_log("Error en get_data.php: " . $e->getMessage());
    echo json_encode([
        'error' => true,
        'message' => 'Se ha producido un error al obtener los datos.',
        'details' => [
            'errorMessage' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]
    ]);
    exit();
}
