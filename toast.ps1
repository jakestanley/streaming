$toastXml = @"
<toast activationType="foreground">
    <visual>
        <binding template="ToastGeneric">
            <text>Custom Notification</text>
            <text>This is a custom notification message.</text>
        </binding>
    </visual>
    <actions>
        <action
            activationType="foreground"
            content="OK"
            arguments="action=ok" />
        <action
            activationType="foreground"
            content="Cancel"
            arguments="action=cancel" />
    </actions>
</toast>
"@

$toast = New-Object -ComObject "Shell.Application"
$toastNamespace = $toast.Namespace("shell:notifications")

# Display the notification
$toastNamespace.CreateToastNotification($toastXml).Show()